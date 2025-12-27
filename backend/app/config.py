from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://codereview:codereview_pass@localhost:5432/codereview_db"
    
    # GitHub App
    github_app_id: str = "123456"
    github_app_private_key_path: str = "./keys/test.pem"
    github_webhook_secret: str = "test_secret"
    
    # LLM API
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    llm_provider: str = "openai"  # openai, anthropic, or google
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    jwt_secret_key: str = "dev_secret_key_for_testing"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = "development"
    api_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    
    # Error Tracking
    sentry_dsn: Optional[str] = None
    sentry_traces_sample_rate: float = 0.1  # 10% of transactions
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Analysis Config
    max_files_per_analysis: int = 50
    max_lines_per_llm_call: int = 500
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
