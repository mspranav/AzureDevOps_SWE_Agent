"""
Database configuration and connection management
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
async_session_factory = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False, 
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with async_session_factory() as session:
        logger.debug("Database session created")
        try:
            yield session
            await session.commit()
            logger.debug("Database session committed")
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rolled back: {str(e)}")
            raise
        finally:
            await session.close()
            logger.debug("Database session closed")