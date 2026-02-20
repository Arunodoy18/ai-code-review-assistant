"""
Production-ready logging configuration.

Provides structured logging with proper levels, no secrets leakage,
and support for correlation IDs for request tracing.
"""

import logging
import sys
from typing import Any
from app.config import settings


class SanitizingFormatter(logging.Formatter):
    """Custom formatter that sanitizes sensitive information from logs."""
    
    SENSITIVE_KEYS = [
        'password', 'token', 'secret', 'api_key', 'private_key',
        'authorization', 'jwt', 'credentials', 'apikey'
    ]
    
    def format(self, record: logging.LogRecord) -> str:
        # Sanitize message
        if isinstance(record.msg, dict):
            record.msg = self._sanitize_dict(record.msg)
        elif isinstance(record.msg, str):
            record.msg = self._sanitize_string(record.msg)
        
        return super().format(record)
    
    def _sanitize_dict(self, data: dict) -> dict:
        """Remove sensitive keys from dictionary."""
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_KEYS):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def _sanitize_string(self, text: str) -> str:
        """Basic string sanitization."""
        # Don't log potential tokens/keys
        for sensitive in self.SENSITIVE_KEYS:
            if sensitive in text.lower():
                return f"Log message redacted (contains: {sensitive})"
        return text


def setup_logging():
    """Configure production-ready logging."""
    
    # Determine log level based on environment
    # Use LOG_LEVEL env var if set, otherwise INFO for all environments
    import os
    env_log_level = os.getenv("LOG_LEVEL", "").upper()
    if env_log_level and hasattr(logging, env_log_level):
        log_level = getattr(logging, env_log_level)
    else:
        log_level = logging.INFO
    
    # Create formatters
    if settings.is_production:
        # JSON-like structured logging for production
        log_format = '{"time":"%(asctime)s", "level":"%(levelname)s", "name":"%(name)s", "message":"%(message)s", "path":"%(pathname)s", "line":%(lineno)d}'
    else:
        # Human-readable for development
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = SanitizingFormatter(
        log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set levels for third-party loggers
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING if settings.is_production else logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('passlib').setLevel(logging.WARNING)
    logging.getLogger('multipart').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    # Force uvicorn loggers to use our stdout handler instead of their default
    # stderr handler (which PowerShell renders in red).
    for uv_name in ('uvicorn', 'uvicorn.error', 'uvicorn.access'):
        uv_logger = logging.getLogger(uv_name)
        uv_logger.handlers.clear()
        uv_logger.addHandler(console_handler)
        uv_logger.propagate = False
    
    # Log startup info
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.environment} environment")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    
    return logger


# Uvicorn-compatible logging config that sends everything to stdout instead of
# stderr (which PowerShell renders in red).  Used by main.py and the Dockerfile
# entrypoint to override uvicorn's default logging behaviour.
UVICORN_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - uvicorn - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(asctime)s - uvicorn.access - INFO - %(client_addr)s - \"%(request_line)s\" %(status_code)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}


# Initialize logging on import
logger = setup_logging()
