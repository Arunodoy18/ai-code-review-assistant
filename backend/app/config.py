from pydantic_settings import BaseSettings
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://codereview:codereview_pass@localhost:5432/codereview_db")
    
    # GitHub App
    github_app_id: str = os.getenv("GITHUB_APP_ID", "123456")
    github_app_private_key_path: str = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH", "./keys/test.pem")
    github_webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "test_secret")
    
    # LLM API
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev_secret_key_for_testing")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    api_port: int = int(os.getenv("PORT", "8000"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Error Tracking
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    sentry_traces_sample_rate: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    
    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Analysis Config
    max_files_per_analysis: int = int(os.getenv("MAX_FILES_PER_ANALYSIS", "50"))
    max_lines_per_llm_call: int = int(os.getenv("MAX_LINES_PER_LLM_CALL", "500"))
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev"]
    
    def validate_production_requirements(self) -> list[str]:
        """Validate required environment variables for production."""
        errors = []
        
        if self.is_production:
            if self.jwt_secret_key == "dev_secret_key_for_testing":
                errors.append("JWT_SECRET_KEY must be set in production")
            if self.github_webhook_secret == "test_secret":
                errors.append("GITHUB_WEBHOOK_SECRET must be set in production")
            if not self.sentry_dsn:
                logger.warning("SENTRY_DSN not set - error tracking disabled in production")
            if "localhost" in self.database_url:
                errors.append("DATABASE_URL cannot point to localhost in production")
            if "localhost" in self.redis_url:
                errors.append("REDIS_URL cannot point to localhost in production")
        
        return errors
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Validate production requirements on import
if settings.is_production:
    validation_errors = settings.validate_production_requirements()
    if validation_errors:
        error_msg = "\n".join([f"  - {err}" for err in validation_errors])
        logger.error(f"Production configuration errors:\n{error_msg}")
        # In strict production mode, you might want to raise an exception here
        # raise RuntimeError(f"Production configuration invalid:\n{error_msg}")
