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


class Settings(BaseSettings):
    """Application runtime configuration with local-first defaults."""

    # Database
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL))
    
    # GitHub App
    github_app_id: str = Field(default=os.getenv("GITHUB_APP_ID", ""))
    github_app_private_key_path: Optional[str] = Field(default=os.getenv("GITHUB_APP_PRIVATE_KEY_PATH"))
    github_app_private_key_b64: Optional[str] = Field(default=os.getenv("GITHUB_APP_PRIVATE_KEY_B64"))
    github_webhook_secret: str = Field(default=os.getenv("GITHUB_WEBHOOK_SECRET", ""))
    enable_github_integration: bool = Field(default=os.getenv("ENABLE_GITHUB_INTEGRATION", "false").lower() in {"1", "true", "yes"})
    enable_github_webhooks: bool = Field(default=os.getenv("ENABLE_GITHUB_WEBHOOKS", "false").lower() in {"1", "true", "yes"})
    
    # LLM API
    openai_api_key: Optional[str] = Field(default=os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default=os.getenv("ANTHROPIC_API_KEY"))
    google_api_key: Optional[str] = Field(default=os.getenv("GOOGLE_API_KEY"))
    groq_api_key: Optional[str] = Field(default=os.getenv("GROQ_API_KEY"))
    groq_model: str = Field(default=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    llm_provider: str = Field(default=os.getenv("LLM_PROVIDER", "groq"))
    
    # Redis
    redis_url: str = Field(default=os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    enable_background_tasks: bool = Field(default=os.getenv("ENABLE_BACKGROUND_TASKS", "false").lower() in {"1", "true", "yes"})
    
    # JWT
    jwt_secret_key: str = Field(default=os.getenv("JWT_SECRET_KEY", "dev_secret_key_for_testing"))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    port: int = Field(default=int(os.getenv("PORT", "8000")))
    frontend_url: str = Field(default=os.getenv("FRONTEND_URL", "http://localhost:5173"))
    
    # Error Tracking
    sentry_dsn: Optional[str] = Field(default=os.getenv("SENTRY_DSN"))
    sentry_traces_sample_rate: float = Field(default=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")))
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")))
    
    # Analysis Config
    max_files_per_analysis: int = Field(default=int(os.getenv("MAX_FILES_PER_ANALYSIS", "50")))
    max_lines_per_llm_call: int = Field(default=int(os.getenv("MAX_LINES_PER_LLM_CALL", "500")))

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
        if not self.openai_api_key:
            warnings.append("OPENAI_API_KEY not detected; AI analysis features will return empty results.")
        if self.uses_sqlite:
            logger.info("Using local SQLite database located at %s", self.database_url)
        return warnings

    def validate_production_requirements(self) -> list[str]:
        """Validate required environment variables for production."""
        errors = []
        
        if self.is_production:
            if self.jwt_secret_key == "dev_secret_key_for_testing":
                errors.append("JWT_SECRET_KEY must be set in production")
            if not self.github_webhook_secret:
                errors.append("GITHUB_WEBHOOK_SECRET must be set in production")
            if self.enable_github_integration:
                if not self.github_app_id:
                    errors.append("GITHUB_APP_ID must be configured when GitHub integration is enabled")
                if not self.resolve_github_private_key_path():
                    errors.append("GitHub App private key must be provided via path or base64")
            if not self.openai_api_key:
                errors.append("OPENAI_API_KEY must be set in production")
            if not self.sentry_dsn:
                logger.warning("SENTRY_DSN not set - error tracking disabled in production")
            if "localhost" in self.database_url or "127.0.0.1" in self.database_url:
                errors.append("DATABASE_URL cannot point to localhost in production")
            if "localhost" in self.redis_url or "127.0.0.1" in self.redis_url:
                errors.append("REDIS_URL cannot point to localhost in production")
        
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
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Validate requirements on import
if settings.is_production:
    validation_errors = settings.validate_production_requirements()
    if validation_errors:
        error_msg = "\n".join([f"  - {err}" for err in validation_errors])
        logger.error(f"PRODUCTION CONFIGURATION ERRORS:\n{error_msg}")
        # We don't raise here to allow the app to start and potentially show errors via API
else:
    validation_warnings = settings.validate_development_requirements()
    if validation_warnings:
        warning_msg = "\n".join([f"  - {warn}" for warn in validation_warnings])
        logger.warning(f"DEVELOPMENT CONFIGURATION WARNINGS:\n{warning_msg}")
