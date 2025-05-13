"""
API routes package initialization
"""

from fastapi import APIRouter

from app.api.routes.task import router as task_router
from app.api.routes.repository import router as repository_router
from app.api.routes.code_generation import router as code_generation_router
from app.api.routes.pull_request import router as pull_request_router

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(task_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(repository_router, prefix="/repositories", tags=["repositories"])
api_router.include_router(code_generation_router, prefix="/code", tags=["code-generation"])
api_router.include_router(pull_request_router, prefix="/prs", tags=["pull-requests"])