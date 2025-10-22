"""
Database session management with mode-aware configuration.

Supports:
- Dev Mode: Local PostgreSQL (minimal setup)
- Cloud Mode: Supabase PostgreSQL (optimized for serverless)
"""

from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# ============================================================================
# DATABASE ENGINE FACTORY
# ============================================================================


def _get_database_url() -> str:
    """Get database URL based on execution mode."""
    db_url = str(settings.DATABASE_URL)

    # Ensure async driver
    if "postgresql://" in db_url and "asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    elif "postgresql+psycopg2://" in db_url:
        db_url = db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

    return db_url


def _create_engine():
    """Create async SQLAlchemy engine based on mode."""
    database_url = _get_database_url()

    # Mode-specific engine configuration
    if settings.is_dev_mode:
        # Dev mode: Simple configuration
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
        )
    else:
        # Cloud mode: Optimized for Supabase (serverless)
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            # Connection pooling tuned for serverless
            pool_recycle=300,  # Recycle connections every 5 minutes
            connect_args={
                "timeout": 20,
                "server_settings": {
                    "application_name": "raptorflow",
                }
            }
        )

    return engine


# Create async engine
engine = _create_engine()

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Automatically handles transaction management based on execution mode.

    Usage:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
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
    """Initialize database (create tables, migrations, etc)."""
    async with engine.begin() as conn:
        # In production, use Alembic for migrations
        # For dev mode, can auto-create tables
        if settings.is_dev_mode:
            await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
