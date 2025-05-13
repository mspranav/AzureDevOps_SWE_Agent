"""
Task API schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, UUID4


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskRequirements(BaseModel):
    """
    Task requirements schema
    """
    files_to_modify: Optional[List[str]] = None
    testing_required: Optional[bool] = None
    additional_context: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields for flexibility


class TaskBase(BaseModel):
    """
    Base task schema
    """
    azure_devops_id: str = Field(..., description="ID of the task in Azure DevOps")
    organization: str = Field(..., description="Azure DevOps organization")
    project: str = Field(..., description="Azure DevOps project")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Optional[int] = Field(0, description="Task priority (higher = higher priority)")
    requirements: Optional[TaskRequirements] = Field(None, description="Task requirements")


class TaskCreate(TaskBase):
    """
    Task creation schema
    """
    pass


class TaskUpdate(BaseModel):
    """
    Task update schema - all fields optional
    """
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    requirements: Optional[TaskRequirements] = None
    repository_id: Optional[UUID4] = None
    metadata: Optional[Dict[str, Any]] = None


class RepositorySummary(BaseModel):
    """
    Repository summary schema for task responses
    """
    id: UUID4
    name: str
    url: str


class PullRequestSummary(BaseModel):
    """
    Pull request summary schema for task responses
    """
    id: UUID4
    title: str
    status: str
    url: Optional[str] = None


class TaskRead(TaskBase):
    """
    Task read schema - returned in responses
    """
    id: UUID4
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    repository: Optional[RepositorySummary] = None
    pull_request: Optional[PullRequestSummary] = None
    analysis: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True