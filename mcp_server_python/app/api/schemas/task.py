"""
Task API schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json

from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskRequirements(BaseModel):
    """
    Task requirements schema with structured fields to encourage
    effective task descriptions
    """
    # Technical context
    repository_url: Optional[str] = Field(None, description="URL of the repository to modify")
    files_to_modify: Optional[List[str]] = Field(None, description="List of files that need to be modified")
    directories_to_search: Optional[List[str]] = Field(None, description="List of directories to focus on")
    languages: Optional[List[str]] = Field(None, description="Programming languages relevant for this task")
    frameworks: Optional[List[str]] = Field(None, description="Frameworks used in the codebase")
    
    # Requirements details
    specific_requirements: Optional[List[str]] = Field(None, description="Specific requirements for the implementation")
    testing_required: Optional[bool] = Field(True, description="Whether tests should be created or updated")
    test_frameworks: Optional[List[str]] = Field(None, description="Testing frameworks to use")
    
    # Acceptance criteria
    acceptance_criteria: Optional[List[str]] = Field(None, description="Specific conditions that must be met")
    performance_requirements: Optional[str] = Field(None, description="Performance expectations if applicable")
    
    # Dependencies
    related_tasks: Optional[List[str]] = Field(None, description="IDs of related tasks")
    dependent_systems: Optional[List[str]] = Field(None, description="External systems or services that are relevant")
    
    # Additional context
    additional_context: Optional[str] = Field(None, description="Any additional context that might be helpful")
    do_not_modify: Optional[List[str]] = Field(None, description="Files or components that should not be changed")
    examples: Optional[str] = Field(None, description="Examples to clarify the expected behavior")
    
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
    repository_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RepositorySummary(BaseModel):
    """
    Repository summary schema for task responses
    """
    id: str
    name: str
    url: str


class PullRequestSummary(BaseModel):
    """
    Pull request summary schema for task responses
    """
    id: str
    title: str
    status: str
    url: Optional[str] = None


class TaskRead(TaskBase):
    """
    Task read schema - returned in responses
    """
    id: str
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
    
    @validator("analysis", "result", "metadata", pre=True)
    def parse_json(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v
    
    class Config:
        orm_mode = True