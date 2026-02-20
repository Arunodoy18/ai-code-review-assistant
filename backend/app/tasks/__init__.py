import os

from app.config import str_to_bool

# Only create Celery app if background tasks are enabled.
# Otherwise provide a stub so that @celery_app.task decorators still work
# but tasks run synchronously via the inline fallback in analysis.py.
_background_enabled = str_to_bool(os.getenv("ENABLE_BACKGROUND_TASKS"))

if _background_enabled:
    try:
        from celery import Celery
        from app.config import settings

        celery_app = Celery(
            "codereview",
            broker=settings.redis_url,
            backend=settings.redis_url,
        )

        celery_app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            task_track_started=True,
            task_time_limit=600,
            task_soft_time_limit=540,
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            "Celery/Redis initialization failed (falling back to stub): %s", e
        )
        _background_enabled = False  # fall through to stub below

if not _background_enabled:
    # Lightweight stub — the .task() decorator simply returns the original function
    class _CeleryStub:
        """Minimal stub so @celery_app.task(...) works without a broker."""
        def task(self, *args, **kwargs):
            def decorator(fn):
                fn.delay = lambda *a, **kw: (_ for _ in ()).throw(
                    RuntimeError("Background tasks are disabled")
                )
                return fn
            # Support @celery_app.task and @celery_app.task(...)
            if args and callable(args[0]):
                return decorator(args[0])
            return decorator

    celery_app = _CeleryStub()
