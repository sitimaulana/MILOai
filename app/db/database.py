"""
MILO AI Backend - Database Connection

Async SQLAlchemy engine + session factory for MySQL (with SQLite / PostgreSQL fallback).
"""

import logging
from sqlalchemy.engine.url import make_url
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

# Async engine for FastAPI route handlers
# Detect database dialect: SQLite vs MySQL vs PostgreSQL
_is_sqlite = settings.database_url.startswith("sqlite")
_is_mysql = settings.database_url.startswith("mysql")

engine_kwargs = dict(
    echo=settings.debug,
)

if not _is_sqlite:
    # Connection pool settings for MySQL / PostgreSQL
    engine_kwargs.update(
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    if _is_mysql:
        # Recycle idle connections to prevent MySQL 2006 "server has gone away" error
        engine_kwargs.update(
            pool_recycle=3600,
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


async def _ensure_mysql_db_exists() -> None:
    """Auto-create MySQL database if it does not exist yet (e.g. in XAMPP / Laragon)."""
    try:
        url = make_url(settings.database_url)
        db_name = url.database
        if not db_name:
            return

        server_url = url.set(database="mysql")
        temp_engine = create_async_engine(server_url, isolation_level="AUTOCOMMIT")
        async with temp_engine.connect() as conn:
            await conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            )
        await temp_engine.dispose()
        logger.info(f"Verified MySQL database '{db_name}' exists.")
    except Exception as e:
        logger.warning(f"Could not auto-create MySQL database (it may already exist or require manual creation): {e}")


async def _migrate_columns(conn) -> None:
    """Ensure any newly added schema columns exist in existing database tables."""
    try:
        res = await conn.execute(text("SHOW COLUMNS FROM users LIKE 'placement_score'"))
        if not res.fetchone():
            await conn.execute(text("ALTER TABLE users ADD COLUMN placement_score FLOAT NULL"))
            logger.info("Migrated: added 'placement_score' column to 'users' table.")
    except Exception as e:
        logger.warning(f"Column migration check failed (non-critical): {e}")


async def init_db() -> None:
    """Create all tables on startup (for dev/testing/production)."""
    if _is_mysql:
        await _ensure_mysql_db_exists()

    async with engine.begin() as conn:
        from app.db import models  # noqa: F401 — import models to register them
        await conn.run_sync(Base.metadata.create_all)
        if _is_mysql:
            await _migrate_columns(conn)
