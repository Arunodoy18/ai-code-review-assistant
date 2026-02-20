import os

# Only create Celery app if background tasks are enabled.
# Otherwise provide a stub so that @celery_app.task decorators still work
# but tasks run synchronously via the inline fallback in analysis.py.
_background_enabled = os.getenv("ENABLE_BACKGROUND_TASKS", "false").lower() in {"1", "true", "yes"}

if _background_enabled:
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
else:
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
