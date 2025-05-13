"""
Repository API routes
"""

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_logger
from app.core.database import get_db
from app.models.repository import Repository
from app.utils.exceptions import NotFoundException
from app.utils.logger import Logger

# Create router
router = APIRouter()


@router.get("/")
async def read_repositories(
    organization: Optional[str] = None,
    project: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get all repositories, with optional filtering
    """
    logger.info("Fetching repositories", 
                user_id=current_user["id"], 
                organization=organization, 
                project=project)
    
    # Build query
    query = select(Repository)
    
    # Apply filters
    if organization:
        query = query.filter(Repository.organization == organization)
    if project:
        query = query.filter(Repository.project == project)
    
    # Order by name
    query = query.order_by(Repository.name)
    
    # Paginate results
    result = await paginate(db, query)
    
    # Convert to dictionary for response
    return {
        "items": [repo.dict() for repo in result.items],
        "total": result.total,
        "page": result.page,
        "size": result.size,
        "pages": result.pages
    }


@router.get("/{repo_id}")
async def read_repository(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get a specific repository by ID
    """
    logger.info("Fetching repository", user_id=current_user["id"], repo_id=repo_id)
    
    # Get repository
    result = await db.execute(select(Repository).filter(Repository.id == repo_id))
    db_repo = result.scalars().first()
    
    if not db_repo:
        logger.warning("Repository not found", repo_id=repo_id)
        raise NotFoundException(f"Repository with ID {repo_id} not found")
    
    return db_repo.dict()


# Add pagination to router
add_pagination(router)