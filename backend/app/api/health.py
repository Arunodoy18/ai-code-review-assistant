from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db, engine
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check - always returns 200 if app is running."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Code Review Assistant",
        "environment": settings.environment,
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check with comprehensive dependency validation.
    
    Used by container orchestration to determine if app is ready for traffic.
    Returns 503 if any critical dependency is unavailable.
    """
    health_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
        "checks": {}
    }
    
    all_healthy = True
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
        logger.debug("Database health check: OK")
    except Exception as e:
        all_healthy = False
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis (non-critical - for caching only)
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        redis_client.ping()
        redis_client.close()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
        logger.debug("Redis health check: OK")
    except Exception as e:
        # Don't fail readiness for Redis
        health_status["checks"]["redis"] = {
            "status": "degraded",
            "message": f"Redis unavailable (non-critical): {str(e)}"
        }
        logger.warning(f"Redis health check failed (non-critical): {e}")
    
    # Fail if critical dependencies are down
    if not all_healthy:
        health_status["status"] = "not_ready"
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@router.get("/live")
async def liveness_check():
    """Liveness check - indicates if app is alive and not deadlocked.
    
    Used by container orchestration to determine if app should be restarted.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
