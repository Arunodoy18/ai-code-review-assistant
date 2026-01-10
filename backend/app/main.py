from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.api import webhooks, analysis, projects, health, config
from app.middleware.cache import ResponseCacheMiddleware
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# CORS - Production-ready configuration
origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "https://codereview-frontend.jollysea-c5c0b121.centralus.azurecontainerapps.io",
]

# Allow frontend URL from settings if provided
if settings.frontend_url and settings.frontend_url not in origins:
    origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(config.router, prefix="/api", tags=["configuration"])


@app.get("/")
async def root():
    return {
        "message": "AI Code Review Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }
