"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator

from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Use SQLite for development if PostgreSQL is not available
import os

# Determine database URL
if settings.environment == "development":
    # Use SQLite for development
    sqlite_path = os.path.join(os.getcwd(), "webex_calling.db")
    database_url = f"sqlite:///{sqlite_path}"
    async_database_url = f"sqlite+aiosqlite:///{sqlite_path}"
    logger.info(f"Using SQLite database: {sqlite_path}")
else:
    # Use PostgreSQL for production
    database_url = settings.database_url
    async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Sync Engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=settings.environment == "development",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Engine for FastAPI
async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    echo=settings.environment == "development",
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Sync dependency
@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get database session (sync)

    Usage:
        with get_db() as db:
            # Use db
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Async dependency for FastAPI
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session for FastAPI

    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_async_db)):
            # Use db
            pass
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


def init_db():
    """Initialize database (create all tables)"""
    from src.models import Base

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


async def init_db_async():
    """Initialize database asynchronously (non-blocking if DB unavailable)"""
    try:
        from src.models import Base

        logger.info("Creating database tables (async)...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed (will continue without DB): {e}")
        logger.warning("The API will start but database-dependent endpoints may not work")
