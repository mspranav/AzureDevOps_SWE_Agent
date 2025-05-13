"""
Task API routes
"""

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_logger
from app.api.schemas.task import (
    TaskCreate, 
    TaskRead, 
    TaskStatus, 
    TaskUpdate
)
from app.core.database import get_db
from app.models.task import Task
from app.utils.exceptions import NotFoundException
from app.utils.logger import Logger

# Create router
router = APIRouter()


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Create a new task
    """
    logger.info("Creating new task", user_id=current_user["id"])
    
    # Create new task model
    db_task = Task(
        azure_devops_id=task_in.azure_devops_id,
        organization=task_in.organization,
        project=task_in.project,
        title=task_in.title,
        description=task_in.description,
        status=TaskStatus.PENDING.value,
        priority=task_in.priority,
        requirements=json.dumps(task_in.requirements.dict() if task_in.requirements else {}),
    )
    
    # Save to database
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    
    logger.info("Task created successfully", task_id=str(db_task.id))
    return db_task


@router.get("/", response_model=Page[TaskRead])
async def read_tasks(
    organization: Optional[str] = None,
    project: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get all tasks, with optional filtering
    """
    logger.info("Fetching tasks", 
                user_id=current_user["id"], 
                organization=organization, 
                project=project, 
                status=status)
    
    # Build query
    query = select(Task)
    
    # Apply filters
    if organization:
        query = query.filter(Task.organization == organization)
    if project:
        query = query.filter(Task.project == project)
    if status:
        query = query.filter(Task.status == status.value)
    
    # Order by priority and creation date
    query = query.order_by(Task.priority.desc(), Task.created_at.desc())
    
    # Paginate results
    return await paginate(db, query)


@router.get("/{task_id}", response_model=TaskRead)
async def read_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get a specific task by ID
    """
    logger.info("Fetching task", user_id=current_user["id"], task_id=task_id)
    
    # Get task
    result = await db.execute(select(Task).filter(Task.id == task_id))
    db_task = result.scalars().first()
    
    if not db_task:
        logger.warning("Task not found", task_id=task_id)
        raise NotFoundException(f"Task with ID {task_id} not found")
    
    return db_task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Update a task
    """
    logger.info("Updating task", user_id=current_user["id"], task_id=task_id)
    
    # Get task
    result = await db.execute(select(Task).filter(Task.id == task_id))
    db_task = result.scalars().first()
    
    if not db_task:
        logger.warning("Task not found", task_id=task_id)
        raise NotFoundException(f"Task with ID {task_id} not found")
    
    # Update fields
    update_data = task_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "requirements" and value is not None:
            setattr(db_task, field, json.dumps(value.dict()))
        elif field == "status" and value is not None:
            setattr(db_task, field, value.value)
        elif field == "metadata" and value is not None:
            setattr(db_task, field, json.dumps(value))
        else:
            setattr(db_task, field, value)
    
    # Save changes
    await db.commit()
    await db.refresh(db_task)
    
    logger.info("Task updated successfully", task_id=task_id)
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> None:
    """
    Delete a task
    """
    logger.info("Deleting task", user_id=current_user["id"], task_id=task_id)
    
    # Get task
    result = await db.execute(select(Task).filter(Task.id == task_id))
    db_task = result.scalars().first()
    
    if not db_task:
        logger.warning("Task not found", task_id=task_id)
        raise NotFoundException(f"Task with ID {task_id} not found")
    
    # Delete task
    await db.delete(db_task)
    await db.commit()
    
    logger.info("Task deleted successfully", task_id=task_id)


# Add pagination to router
add_pagination(router)