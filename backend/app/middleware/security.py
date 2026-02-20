"""
Security middleware and configurations for Phase 3A.

HTTPS enforcement, security headers, rate limiting, and security best practices.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (CSP)
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Needed for React/Vite
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.groq.com https://api.openai.com https://api.anthropic.com; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Remove server header for security obscurity
        response.headers.pop("Server", None)
        
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP to HTTPS in production."""
    
    async def dispatch(self, request: Request, call_next):
        if settings.is_production:
            # Skip HTTPS redirect for health checks (Render probes internally over HTTP)
            if request.url.path in ("/api/health", "/health", "/"):
                return await call_next(request)
            # Check if request is HTTP (not HTTPS)
            if request.url.scheme != "https":
                # Check X-Forwarded-Proto header (for reverse proxies)
                forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
                if forwarded_proto != "https":
                    # Redirect to HTTPS
                    https_url = request.url.replace(scheme="https")
                    return Response(
                        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                        headers={"Location": str(https_url)}
                    )
        
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)  # IP -> [timestamps]
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down.",
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.requests_per_minute - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(minutes=1)).timestamp()))
        
        return response


def configure_cors(app):
    """Configure CORS middleware with security best practices."""
    allowed_origins = []
    
    if settings.is_production:
        # In production, only allow specific origins
        allowed_origins = [
            settings.frontend_url,
            "https://app.codereview.ai",  # Production domain
            "https://www.codereview.ai",
        ]
    else:
        # In development, allow localhost
        allowed_origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )


def validate_email_security():
    """Validate email configuration for security."""
    if not settings.enable_email:
        logger.warning("Email is disabled. Users cannot verify emails or reset passwords.")
        return
    
    if settings.is_production:
        if not settings.smtp_username or not settings.smtp_password:
            logger.error("SMTP credentials not configured in production!")
        
        if settings.smtp_host == "smtp.gmail.com" and not settings.smtp_password:
            logger.warning("Gmail SMTP detected but no app password configured. Use App Passwords, not your account password!")
        
        if settings.smtp_port not in [465, 587]:
            logger.warning(f"Non-standard SMTP port {settings.smtp_port}. Use 587 (STARTTLS) or 465 (SSL/TLS).")


def validate_jwt_security():
    """Validate JWT configuration for security."""
    if settings.jwt_secret_key == "dev_secret_key_for_testing":
        if settings.is_production:
            logger.error("CRITICAL: Using default JWT secret in production! Set JWT_SECRET_KEY environment variable.")
        else:
            logger.warning("Using development JWT secret. Set JWT_SECRET_KEY for production.")
    
    if len(settings.jwt_secret_key) < 32:
        logger.warning("JWT secret key is too short. Use at least 32 characters for security.")


def validate_https_configuration():
    """Validate HTTPS configuration."""
    if settings.is_production:
        # Support comma-separated frontend URLs
        frontend_urls = [url.strip() for url in settings.frontend_url.split(",") if url.strip()]
        for url in frontend_urls:
            if not url.startswith("https://"):
                logger.warning(f"FRONTEND_URL '{url}' should use HTTPS in production")
            if "localhost" in url or "127.0.0.1" in url:
                logger.warning(f"FRONTEND_URL '{url}' points to localhost in production")


def run_security_validation():
    """Run all security validations on startup."""
    logger.info("Running Phase 3A security validations...")
    
    validate_email_security()
    validate_jwt_security()
    validate_https_configuration()
    
    logger.info("Security validation complete.")


# Security recommendations for production deployment
PRODUCTION_SECURITY_CHECKLIST = """
Phase 3A Production Security Checklist:

✅ Environment Configuration:
  - Set JWT_SECRET_KEY to a strong random string (32+ characters)
  - Set SMTP credentials for email functionality
  - Set FRONTEND_URL to production HTTPS domain
  - Ensure DATABASE_URL uses SSL/TLS connection
  - Ensure REDIS_URL uses password authentication

✅ Database Security:
  - Enable SSL/TLS for PostgreSQL connections
  - Use strong database passwords
  - Restrict database access to application servers only
  - Enable database backups and encryption at rest
  - Regular security updates for database software

✅ HTTPS/TLS:
  - Obtain valid SSL/TLS certificate (Let's Encrypt recommended)
  - Configure web server (nginx/Apache) for HTTPS only
  - Enable HTTP → HTTPS redirect
  - Use HSTS (Strict-Transport-Security header)
  - Configure TLS 1.2+ only (disable TLS 1.0/1.1)

✅ Email Security:
  - Use SMTP over TLS (port 587) or SSL (port 465)
  - For Gmail: Use App Passwords, not account password
  - Verify SPF/DKIM/DMARC records for your domain
  - Monitor email delivery rates and spam complaints

✅ Password Security:
  - Passwords are hashed with bcrypt (already implemented)
  - Enforce minimum 6 characters (consider increasing to 8+)
  - Consider adding password complexity requirements
  - Implement account lockout after failed login attempts

✅ API Key Security:
  - API keys are encrypted in database (already implemented)
  - Rotate API keys regularly
  - Use environment variables, never hardcode secrets
  - Implement API key permission scoping

✅ Rate Limiting:
  - Rate limiting middleware enabled (already implemented)
  - Configure appropriate limits for your traffic
  - Monitor for abuse patterns
  - Consider using Redis for distributed rate limiting

✅ Logging & Monitoring:
  - Enable Sentry for error tracking
  - Log all authentication events (login, logout, password reset)
  - Monitor for suspicious activity (rapid login attempts, etc.)
  - Set up alerts for critical errors
  - Regularly review logs for security incidents

✅ Backup & Recovery:
  - Daily database backups
  - Test backup restoration regularly
  - Encrypt backups
  - Store backups in separate location
  - Document disaster recovery procedures

✅ Dependencies:
  - Keep all dependencies up to date
  - Run `pip  list --outdated` regularly
  - Subscribe to security advisories for key dependencies
  - Use Dependabot or similar for automated updates

✅ Compliance:
  - GDPR data export/delete implemented (already done)
  - Privacy Policy published (already done)
  - Terms of Service published (already done)
  - Cookie consent banner (add if using analytics)
  - Document data processing activities
"""
