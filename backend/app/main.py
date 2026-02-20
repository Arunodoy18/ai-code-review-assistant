from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import engine, Base
from app.api import webhooks, analysis, projects, health, config, auth, phase2, auth_phase3a, billing
from app.middleware.cache import ResponseCacheMiddleware
from app.middleware.security import (
    SecurityHeadersMiddleware,
    HTTPSRedirectMiddleware,
    run_security_validation
)
from app.logging_config import setup_logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Initialize logging first
logger = setup_logging()

# Initialize Sentry
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=0.1,
        send_default_pii=False,
    )
    logger.info("Sentry initialized for error tracking")

# Create database tables on startup
Base.metadata.create_all(bind=engine)
logger.info("Database tables created/verified")

app = FastAPI(
    title="AI Code Review Assistant",
    description="Intelligent code review platform using ML to analyze PRs",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - Support multiple frontend URLs (comma-separated in FRONTEND_URL env var)
_frontend_origins = [url.strip() for url in settings.frontend_url.split(",") if url.strip()]
_allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:8000",
] + _frontend_origins
logger.info(f"CORS allowed origins: {_allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Phase 3A: Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(HTTPSRedirectMiddleware)

# Database validation on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    try:
        # Validate database connectivity
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connectivity validated successfully")
    except Exception as e:
        logger.error(f"FATAL: Database connectivity check failed: {e}")
        # In production, we might want to exit here, but for now just log
    
    # Phase 3A: Run security validation
    run_security_validation()

# Response caching
app.add_middleware(ResponseCacheMiddleware)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(auth_phase3a.router, prefix="/api/auth", tags=["authentication", "phase3a"])
app.include_router(billing.router, tags=["billing"])  # Phase 3B: Billing endpoints
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(config.router, prefix="/api", tags=["configuration"])
app.include_router(phase2.router, prefix="/api/phase2", tags=["phase2-features"])


@app.get("/")
async def root():
    return {
        "message": "AI Code Review Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }
