from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings


def _generate_engine():
    """Create SQLAlchemy engine with sensible defaults for local SQLite"""
    connect_args = {}
    if settings.uses_sqlite:
        connect_args = {"check_same_thread": False}
    return create_engine(
        settings.database_url,
        connect_args=connect_args,
        pool_pre_ping=not settings.uses_sqlite,
        future=True,
    )


engine = _generate_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
