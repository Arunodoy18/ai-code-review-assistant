from __future__ import annotations

import logging
import os
from base64 import b64decode
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_URL = f"sqlite:///{(BASE_DIR / 'local_dev.db').as_posix()}"

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: PRODUCTION-SAFE ENVIRONMENT LOADING
# ═══════════════════════════════════════════════════════════════════════════
# Load .env ONLY in development - production uses Render environment variables
if os.getenv("ENVIRONMENT", "").strip().lower() != "production":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded .env file for development environment")
    except ImportError:
        logger.warning("python-dotenv not installed, skipping .env loading")
else:
    logger.info("Production environment detected - skipping .env file")


def _get_env(key: str, default: str = "") -> str:
    """Safely get and clean environment variable.
    
    - Strips whitespace
    - Removes trailing slashes for URLs
    - Removes accidental trailing commas
    """
    value = os.getenv(key, default).strip()
    # Remove trailing comma (common typo in env files)
    if value.endswith(","):
        value = value[:-1].strip()
    return value


def str_to_bool(value: str | None, default: bool = False) -> bool:
    """Centralized boolean parsing for environment variables.

    Accepts '1', 'true', 'yes' (case-insensitive) as True.
    Everything else (including None / empty string) returns *default*.
    """
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes"}


def _safe_int(value: str | None, default: int) -> int:
    """Parse an env-var string to int, returning *default* on any failure."""
    if value is None:
        return default
    try:
        return int(value.strip())
    except (ValueError, TypeError, AttributeError):
        return default


class Settings(BaseSettings):
    """Application runtime configuration with local-first defaults."""

    # Database
    database_url: str = Field(default_factory=lambda: _get_env("DATABASE_URL", DEFAULT_SQLITE_URL))
    
    # GitHub App
    github_app_id: str = Field(default_factory=lambda: _get_env("GITHUB_APP_ID", ""))
    github_app_private_key_path: Optional[str] = Field(default_factory=lambda: _get_env("GITHUB_APP_PRIVATE_KEY_PATH") or None)
    github_app_private_key_b64: Optional[str] = Field(default_factory=lambda: _get_env("GITHUB_APP_PRIVATE_KEY_B64") or None)
    github_webhook_secret: str = Field(default_factory=lambda: _get_env("GITHUB_WEBHOOK_SECRET", ""))
    enable_github_integration: bool = Field(default_factory=lambda: str_to_bool(_get_env("ENABLE_GITHUB_INTEGRATION")))
    enable_github_webhooks: bool = Field(default_factory=lambda: str_to_bool(_get_env("ENABLE_GITHUB_WEBHOOKS")))
    
    # LLM API
    openai_api_key: Optional[str] = Field(default_factory=lambda: _get_env("OPENAI_API_KEY") or None)
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: _get_env("ANTHROPIC_API_KEY") or None)
    google_api_key: Optional[str] = Field(default_factory=lambda: _get_env("GOOGLE_API_KEY") or None)
    groq_api_key: Optional[str] = Field(default_factory=lambda: _get_env("GROQ_API_KEY") or None)
    groq_model: str = Field(default_factory=lambda: _get_env("GROQ_MODEL", "llama-3.3-70b-versatile"))
    llm_provider: str = Field(default_factory=lambda: _get_env("LLM_PROVIDER", "groq"))
    
    # Redis
    redis_url: str = Field(default_factory=lambda: _get_env("REDIS_URL", "redis://localhost:6379/0"))
    enable_background_tasks: bool = Field(default_factory=lambda: str_to_bool(_get_env("ENABLE_BACKGROUND_TASKS")))
    
    # JWT
    jwt_secret_key: str = Field(default_factory=lambda: _get_env("JWT_SECRET_KEY", "dev_secret_key_for_testing"))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email (Phase 3A)
    smtp_host: str = Field(default_factory=lambda: _get_env("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = Field(default_factory=lambda: _safe_int(_get_env("SMTP_PORT"), 587))
    smtp_username: Optional[str] = Field(default_factory=lambda: _get_env("SMTP_USERNAME") or None)
    smtp_password: Optional[str] = Field(default_factory=lambda: _get_env("SMTP_PASSWORD") or None)
    smtp_from_email: str = Field(default_factory=lambda: _get_env("SMTP_FROM_EMAIL", "noreply@codereview.ai"))
    smtp_from_name: str = Field(default_factory=lambda: _get_env("SMTP_FROM_NAME", "AI Code Review"))
    enable_email: bool = Field(default_factory=lambda: str_to_bool(_get_env("ENABLE_EMAIL")))
    email_verification_token_expire_hours: int = Field(default_factory=lambda: _safe_int(_get_env("EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS"), 24))
    password_reset_token_expire_hours: int = Field(default_factory=lambda: _safe_int(_get_env("PASSWORD_RESET_TOKEN_EXPIRE_HOURS"), 1))
    
    # Stripe (Phase 3B)
    STRIPE_SECRET_KEY: str = Field(default_factory=lambda: _get_env("STRIPE_SECRET_KEY", ""))
    STRIPE_PUBLISHABLE_KEY: str = Field(default_factory=lambda: _get_env("STRIPE_PUBLISHABLE_KEY", ""))
    STRIPE_WEBHOOK_SECRET: str = Field(default_factory=lambda: _get_env("STRIPE_WEBHOOK_SECRET", ""))
    STRIPE_PRO_MONTHLY_PRICE_ID: str = Field(default_factory=lambda: _get_env("STRIPE_PRO_MONTHLY_PRICE_ID", ""))
    STRIPE_PRO_YEARLY_PRICE_ID: str = Field(default_factory=lambda: _get_env("STRIPE_PRO_YEARLY_PRICE_ID", ""))
    STRIPE_ENTERPRISE_MONTHLY_PRICE_ID: str = Field(default_factory=lambda: _get_env("STRIPE_ENTERPRISE_MONTHLY_PRICE_ID", ""))
    STRIPE_ENTERPRISE_YEARLY_PRICE_ID: str = Field(default_factory=lambda: _get_env("STRIPE_ENTERPRISE_YEARLY_PRICE_ID", ""))
    enable_billing: bool = Field(default_factory=lambda: str_to_bool(_get_env("ENABLE_BILLING")))
    
    # Environment (CRITICAL: Must be read from Render environment variables)
    environment: str = Field(default_factory=lambda: _get_env("ENVIRONMENT", "development"))
    port: int = Field(default_factory=lambda: _safe_int(_get_env("PORT"), 10000))
    frontend_url: str = Field(default_factory=lambda: _get_env("FRONTEND_URL", "http://localhost:5173").rstrip("/"))
    
    # Error Tracking
    sentry_dsn: Optional[str] = Field(default_factory=lambda: _get_env("SENTRY_DSN") or None)
    sentry_traces_sample_rate: float = Field(default=0.1)
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default_factory=lambda: _safe_int(_get_env("RATE_LIMIT_PER_MINUTE"), 60))
    
    # Analysis Config
    max_files_per_analysis: int = Field(default_factory=lambda: _safe_int(_get_env("MAX_FILES_PER_ANALYSIS"), 50))
    max_lines_per_llm_call: int = Field(default_factory=lambda: _safe_int(_get_env("MAX_LINES_PER_LLM_CALL"), 500))

    _resolved_private_key_path: Optional[Path] = None

    @property
    def uses_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev"]
    
    def validate_development_requirements(self) -> list[str]:
        """Validate required environment variables for development."""
        warnings = []
        if self.enable_github_integration:
            if not self.github_app_id:
                warnings.append("GitHub integration enabled but GITHUB_APP_ID is not set")
            if not self.resolve_github_private_key_path():
                warnings.append("GitHub integration enabled but no private key provided (set path or base64 env)")
        # Check configured LLM provider key
        provider = self.llm_provider.lower()
        key_map = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "groq": self.groq_api_key,
        }
        if provider in key_map and not key_map[provider]:
            warnings.append(f"{provider.upper()} API key not detected; AI analysis features will return empty results.")
        if self.uses_sqlite:
            logger.info("Using local SQLite database located at %s", self.database_url)
        return warnings

    def validate_production_requirements(self) -> list[str]:
        """Validate required environment variables for production."""
        errors = []
        
        if self.is_production:
            if self.jwt_secret_key == "dev_secret_key_for_testing":
                errors.append("JWT_SECRET_KEY must be set in production")
            if not self.sentry_dsn:
                logger.warning("SENTRY_DSN not set - error tracking disabled in production")
            if "localhost" in self.database_url or "127.0.0.1" in self.database_url:
                errors.append("DATABASE_URL cannot point to localhost in production")
            # GitHub integration uses per-user PATs (SaaS model), no global GitHub App needed
            if self.enable_github_integration:
                logger.info("GitHub integration enabled (per-user PAT model)")
            # Redis is optional - only warn if background tasks enabled
            if self.enable_background_tasks and ("localhost" in self.redis_url or "127.0.0.1" in self.redis_url):
                logger.warning("REDIS_URL points to localhost but background tasks are enabled")
            # LLM provider check - we support multiple providers, not just OpenAI
            if not any([self.openai_api_key, self.anthropic_api_key, self.google_api_key, self.groq_api_key]):
                logger.warning("No LLM API key configured - users must provide their own")
            # Groq-specific: if provider is groq, key MUST be present
            if self.llm_provider.lower() == "groq" and not self.groq_api_key:
                errors.append("LLM_PROVIDER is 'groq' but GROQ_API_KEY is not set")
        
        return errors

    def resolve_github_private_key_path(self) -> Optional[str]:
        """Return a filesystem path to the GitHub App private key.

        Supports providing the key as a direct path or as a base64-encoded string via
        environment variable. When using the base64 option, the key is written once to
        the system temp directory with restrictive permissions.
        """
        if self.github_app_private_key_path:
            return self.github_app_private_key_path

        if self.github_app_private_key_b64:
            if not self._resolved_private_key_path or not self._resolved_private_key_path.exists():
                try:
                    decoded = b64decode(self.github_app_private_key_b64)
                    temp_dir = Path(gettempdir())
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    temp_path = temp_dir / "github_app_private_key.pem"
                    temp_path.write_bytes(decoded)
                    try:
                        temp_path.chmod(0o600)
                    except PermissionError:
                        logger.warning("Unable to set permissions on %s; ensure container enforces secret security", temp_path)
                    self._resolved_private_key_path = temp_path
                except Exception as exc:
                    logger.error("Failed to decode GitHub App private key: %s", exc)
                    return None
            return str(self._resolved_private_key_path)

        return None

    class Config:
        # Only load .env file in non-production; production relies on real env vars
        env_file = ".env" if os.getenv("ENVIRONMENT", "development").lower() not in ("production", "prod") else None
        case_sensitive = False


settings = Settings()

# Validate requirements on import — log but NEVER sys.exit() so the server can
# bind its port and respond to health checks even with bad configuration.
_config_errors: list[str] = []
if settings.is_production:
    _config_errors = settings.validate_production_requirements()
    if _config_errors:
        error_msg = "\n".join([f"  - {err}" for err in _config_errors])
        logger.critical("PRODUCTION CONFIGURATION ERRORS (server degraded):\n%s", error_msg)
else:
    validation_warnings = settings.validate_development_requirements()
    if validation_warnings:
        warning_msg = "\n".join([f"  - {warn}" for warn in validation_warnings])
        logger.debug("DEVELOPMENT CONFIGURATION NOTES:\n%s", warning_msg)
