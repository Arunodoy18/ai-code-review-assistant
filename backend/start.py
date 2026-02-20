"""Production entrypoint for uvicorn with stdout-only logging."""
import os
import uvicorn
from app.logging_config import UVICORN_LOG_CONFIG

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        log_level="info",
        log_config=UVICORN_LOG_CONFIG,
    )
