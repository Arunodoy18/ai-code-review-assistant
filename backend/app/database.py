from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

_engine = None
_SessionLocal = None

Base = declarative_base()


def _get_engine():
    """Lazy-create SQLAlchemy engine on first use."""
    global _engine
    if _engine is None:
        connect_args = {}
        kwargs: dict = {"future": True}

        if settings.uses_sqlite:
            connect_args = {"check_same_thread": False}
        else:
            # Connection-pool tuning is only valid for pooled (non-SQLite) engines
            kwargs.update(
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_recycle=300,
            )

        _engine = create_engine(
            settings.database_url,
            connect_args=connect_args,
            **kwargs,
        )
    return _engine


def _get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _SessionLocal


def get_db():
    """Dependency for getting database session"""
    Session = _get_session_local()
    db = Session()
    try:
        yield db
    finally:
        db.close()


# Backward-compat: other modules import `engine` and `SessionLocal` directly.
# We expose them as lazy properties via module __getattr__.
def __getattr__(name: str):
    if name == "engine":
        return _get_engine()
    if name == "SessionLocal":
        return _get_session_local()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
