"""
Code Generation API routes
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_logger
from app.core.database import get_db
from app.models.code_generation import CodeGeneration
from app.utils.exceptions import NotFoundException
from app.utils.logger import Logger

# Create router
router = APIRouter()


@router.get("/generations/{generation_id}")
async def read_code_generation(
    generation_id: str,
    include_code: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get a specific code generation by ID
    """
    logger.info("Fetching code generation", 
                user_id=current_user["id"], 
                generation_id=generation_id,
                include_code=include_code)
    
    # Get code generation
    result = await db.execute(select(CodeGeneration).filter(CodeGeneration.id == generation_id))
    db_generation = result.scalars().first()
    
    if not db_generation:
        logger.warning("Code generation not found", generation_id=generation_id)
        raise NotFoundException(f"Code generation with ID {generation_id} not found")
    
    return db_generation.dict(include_code=include_code)


@router.get("/tasks/{task_id}/generations")
async def read_task_code_generations(
    task_id: str,
    include_code: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
) -> Any:
    """
    Get all code generations for a task
    """
    logger.info("Fetching code generations for task", 
                user_id=current_user["id"], 
                task_id=task_id,
                include_code=include_code)
    
    # Get code generations
    result = await db.execute(
        select(CodeGeneration)
        .filter(CodeGeneration.task_id == task_id)
        .order_by(CodeGeneration.language, CodeGeneration.file_path)
    )
    db_generations = result.scalars().all()
    
    return [gen.dict(include_code=include_code) for gen in db_generations]