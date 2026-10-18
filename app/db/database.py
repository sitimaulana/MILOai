"""
MILO AI Backend - Database Connection

Async SQLAlchemy engine + session factory for PostgreSQL.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Async engine for FastAPI route handlers
# Detect if using SQLite (for local dev) vs PostgreSQL (production)
_is_sqlite = settings.database_url.startswith("sqlite")

engine_kwargs = dict(
    echo=settings.debug,
)

if not _is_sqlite:
    # PostgreSQL connection pool settings
    engine_kwargs.update(
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

engine = create_async_engine(settings.database_url, **engine_kwargs)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: yield an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables on startup (for dev/testing)."""
    async with engine.begin() as conn:
        from app.db import models  # noqa: F401 — import models to register them
        await conn.run_sync(Base.metadata.create_all)
