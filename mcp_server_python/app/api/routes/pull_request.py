"""
Pull Request API routes
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_logger
from app.core.database import get_db
from app.models.pull_request import PullRequest
from app.utils.exceptions import NotFoundException
from app.utils.logger import Logger

# Create router
router = APIRouter()


@router.get("/")
async def read_pull_requests(
    repository_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get all pull requests, with optional filtering
    """
    logger.info("Fetching pull requests", 
                user_id=current_user["id"], 
                repository_id=repository_id)
    
    # Build query
    query = select(PullRequest)
    
    # Apply filters
    if repository_id:
        query = query.filter(PullRequest.repository_id == repository_id)
    
    # Order by creation date
    query = query.order_by(PullRequest.created_at.desc())
    
    # Paginate results
    result = await paginate(db, query)
    
    # Convert to dictionary for response
    return {
        "items": [pr.dict() for pr in result.items],
        "total": result.total,
        "page": result.page,
        "size": result.size,
        "pages": result.pages
    }


@router.get("/{pr_id}")
async def read_pull_request(
    pr_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get a specific pull request by ID
    """
    logger.info("Fetching pull request", user_id=current_user["id"], pr_id=pr_id)
    
    # Get pull request
    result = await db.execute(select(PullRequest).filter(PullRequest.id == pr_id))
    db_pr = result.scalars().first()
    
    if not db_pr:
        logger.warning("Pull request not found", pr_id=pr_id)
        raise NotFoundException(f"Pull request with ID {pr_id} not found")
    
    return db_pr.dict()


@router.get("/tasks/{task_id}")
async def read_task_pull_request(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get the pull request for a specific task
    """
    logger.info("Fetching pull request for task", user_id=current_user["id"], task_id=task_id)
    
    # Get pull request
    result = await db.execute(select(PullRequest).filter(PullRequest.task_id == task_id))
    db_pr = result.scalars().first()
    
    if not db_pr:
        logger.warning("Pull request not found for task", task_id=task_id)
        raise NotFoundException(f"Pull request not found for task with ID {task_id}")
    
    return db_pr.dict()


# Add pagination to router
add_pagination(router)