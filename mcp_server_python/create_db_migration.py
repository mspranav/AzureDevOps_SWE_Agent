"""
Script to create initial database schema and tables
"""

import asyncio
import os
import sys
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.models.base import Base, metadata
from app.core.config import settings
from app.models import task, repository, code_generation, pull_request


async def create_schema():
    """Create database schema from SQLAlchemy models"""
    # Create async engine
    engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    
    print("Database schema created successfully!")

    # Close engine
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_schema())