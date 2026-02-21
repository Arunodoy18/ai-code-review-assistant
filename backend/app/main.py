"""
Cloud-safe FastAPI entrypoint.

Design principles:
1. ZERO network I/O at import time.
2. FastAPI app object is created immediately.
3. Guaranteed /api/health endpoint that never depends on external services.
4. All heavy service initialization is offloaded to an async background task
   via ``asyncio.create_task`` so uvicorn can bind the port first.
5. Any service failure is logged — never crashes the process.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# ── Settings & logging (no network I/O, only reads .env / env vars) ───────
from app.config import settings, DEFAULT_SQLITE_URL
from app.logging_config import setup_logging

logger = setup_logging()
logger.info("Module loaded — creating FastAPI app (no network I/O yet)")

# ── Readiness state (toggled by background init) ────────────────────────────
_services_ready = False
_init_errors: list[str] = []

# ──────────────────────────────────────────────────────────────────────────────
# APP CREATION — must be instant, no blocking allowed
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Code Review Assistant",
    description="Intelligent code review platform using ML to analyze PRs",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ── Rate limiting (in-memory, no I/O) ────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS (pure config, no I/O) ──────────────────────────────────────────────
# PHASE 2: BULLETPROOF CORS CONFIGURATION
# ────────────────────────────────────────────────────────────────────────────
# Guaranteed to work with Render + Netlify production deployment

# Get frontend URL from environment and clean it
frontend_url = settings.frontend_url.strip().rstrip("/")

# Build allowed origins list
origins = []

# Always add production frontend if configured
if frontend_url and frontend_url != "http://localhost:5173":
    origins.append(frontend_url)
    logger.info("Added production frontend origin: %s", frontend_url)

# In development, add localhost variants
if not settings.is_production:
    dev_origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:8000",
    ]
    origins.extend(dev_origins)
    logger.info("Development mode - added localhost origins")

# Ensure at least one origin is configured (fallback to localhost in dev)
if not origins:
    origins.append("http://localhost:5173")
    logger.warning("No origins configured, falling back to localhost:5173")

logger.info("CORS allowed origins: %s", origins)
logger.info("CORS configuration: allow_credentials=True, allow_methods=[*], allow_headers=[*]")

# Add CORS middleware BEFORE any routes are registered
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ── Global exception handler ────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Global exception: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ── Security & cache middleware (pure Python imports, no network I/O) ────────
try:
    from app.middleware.cache import ResponseCacheMiddleware
    from app.middleware.security import (
        SecurityHeadersMiddleware,
        HTTPSRedirectMiddleware,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(ResponseCacheMiddleware)
    _middleware_loaded = True
    logger.info("Security & cache middleware loaded")
except Exception as e:
    _middleware_loaded = False
    logger.info("Middleware import failed (non-fatal): %s", e)


# ──────────────────────────────────────────────────────────────────────────────
# GUARANTEED INLINE HEALTH ENDPOINT — always registered, always returns 200
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Basic health check — returns 200 as long as the process is alive."""
    return {
        "status": "healthy" if _services_ready else "starting",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Code Review Assistant",
        "environment": settings.environment,
        "services_ready": _services_ready,
    }


@app.get("/")
async def root():
    return {
        "message": "AI Code Review Assistant API",
        "version": "1.0.0",
        "status": "running",
    }


# ── API routers (imports are now non-blocking after import-safety fixes) ─────
_routers_loaded = True
try:
    from app.api import (
        webhooks, analysis, projects, health, config, auth,
        phase2, auth_phase3a, billing,
    )

    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(auth_phase3a.router, prefix="/api/auth", tags=["authentication", "phase3a"])
    app.include_router(billing.router, tags=["billing"])
    # health router provides /ready and /live — /health is the inline
    # guaranteed endpoint defined above.
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
    app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    app.include_router(config.router, prefix="/api", tags=["configuration"])
    app.include_router(phase2.router, prefix="/api/phase2", tags=["phase2-features"])
    logger.info("API routers loaded successfully")
except Exception as e:
    _routers_loaded = False
    logger.critical(
        "Failed to import API routers (server running degraded): %s", e, exc_info=True
    )


# ──────────────────────────────────────────────────────────────────────────────
# BACKGROUND SERVICE INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────────

async def initialize_services():
    """Heavy initialization — runs as a background task AFTER port binding.

    Every section is wrapped in its own try/except so that a single failing
    dependency never takes down the whole application.
    """
    global _services_ready

    logger.info("Background service initialization starting…")
    
    # ── PHASE 5: CONFIGURATION VALIDATION ─────────────────────────────────
    logger.info("="*70)
    logger.info("CONFIGURATION VALIDATION CHECK")
    logger.info("="*70)
    logger.info("Environment: %s", settings.environment)
    logger.info("Is Production: %s", settings.is_production)
    logger.info("Frontend URL: %s", settings.frontend_url)
    logger.info("CORS Origins: %s", origins)
    logger.info("Database URL: %s", settings.database_url[:30] + "...")
    logger.info("Port: %s", settings.port)
    logger.info("JWT configured: %s", bool(settings.jwt_secret_key and settings.jwt_secret_key != "dev_secret_key_for_testing"))
    logger.info("="*70)
    
    # Validate production configuration
    if settings.is_production:
        validation_errors = []
        
        if settings.jwt_secret_key == "dev_secret_key_for_testing":
            validation_errors.append("JWT_SECRET_KEY is using default dev key in production!")
        
        if not settings.frontend_url or settings.frontend_url == "http://localhost:5173":
            validation_errors.append("FRONTEND_URL is not configured for production!")
        
        if settings.database_url == DEFAULT_SQLITE_URL:
            validation_errors.append("DATABASE_URL is using SQLite in production!")
        
        if validation_errors:
            logger.error("PRODUCTION CONFIGURATION ERRORS:")
            for error in validation_errors:
                logger.error("  - %s", error)
        else:
            logger.info("✓ Production configuration validation passed")

    # ── 1. Sentry (optional, makes a network call) ───────────────────────
    if settings.sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.environment,
                integrations=[FastApiIntegration(), SqlalchemyIntegration()],
                traces_sample_rate=settings.sentry_traces_sample_rate,
                profiles_sample_rate=0.1,
                send_default_pii=False,
            )
            logger.info("Sentry initialized for error tracking")
        except Exception as e:
            _init_errors.append(f"Sentry: {e}")
            logger.warning("Sentry initialization failed (non-fatal): %s", e)
    elif settings.is_production:
        logger.info("SENTRY_DSN not set — error tracking disabled in production")

    # ── 2. Database tables ───────────────────────────────────────────────
    try:
        from app.database import engine, Base

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")

        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connectivity validated")
    except Exception as e:
        _init_errors.append(f"Database: {e}")
        logger.error("Database startup check failed (non-fatal): %s", e)

    # ── 3. Security middleware validation ─────────────────────────────────
    try:
        from app.middleware.security import run_security_validation

        run_security_validation()
        logger.info("Security validation passed")
    except Exception as e:
        _init_errors.append(f"Security: {e}")
        logger.warning("Security validation failed (non-fatal): %s", e)

    # ── Done ─────────────────────────────────────────────────────────────
    _services_ready = True
    if _init_errors:
        logger.warning(
            "Service initialization completed WITH ERRORS:\n  %s",
            "\n  ".join(_init_errors),
        )
    else:
        logger.info("All services initialized successfully")


# ──────────────────────────────────────────────────────────────────────────────
# STARTUP EVENT — kicks off background init, NEVER blocks port binding
# ──────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI startup event — port is binding NOW")

    # ── Fire-and-forget: heavy service init runs in the background ───────
    asyncio.create_task(initialize_services())


# ──────────────────────────────────────────────────────────────────────────────
# LOCAL DEV / DIRECT EXECUTION
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    from app.logging_config import UVICORN_LOG_CONFIG

    port = int(os.environ.get("PORT", "10000"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        log_config=UVICORN_LOG_CONFIG,
    )
