"""
Task model definition
"""

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class TaskStatus(str, enum.Enum):
    """Task status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    """Task model"""
    
    # Columns
    azure_devops_id = Column(String, nullable=False, index=True, unique=True, comment="ID of the task in Azure DevOps")
    organization = Column(String, nullable=False, comment="Azure DevOps organization")
    project = Column(String, nullable=False, comment="Azure DevOps project")
    title = Column(String, nullable=False, comment="Task title")
    description = Column(Text, nullable=True, comment="Task description")
    status = Column(
        Enum(TaskStatus), 
        nullable=False, 
        default=TaskStatus.PENDING,
        index=True,
        comment="Current status of the task"
    )
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repository.id"), nullable=True, comment="ID of the associated repository")
    requirements = Column(JSONB, nullable=False, default={}, comment="JSON object with task requirements")
    analysis = Column(JSONB, nullable=False, default={}, comment="JSON object with task analysis results")
    result = Column(JSONB, nullable=False, default={}, comment="JSON object with task processing results")
    started_at = Column(DateTime, nullable=True, comment="When task processing started")
    completed_at = Column(DateTime, nullable=True, comment="When task processing completed")
    error = Column(Text, nullable=True, comment="Error message if task failed")
    priority = Column(Integer, nullable=False, default=0, comment="Task priority (higher number = higher priority)")
    metadata = Column(JSONB, nullable=False, default={}, comment="Additional metadata for the task")
    
    # Relationships
    repository = relationship("Repository", back_populates="tasks")
    code_generations = relationship("CodeGeneration", back_populates="task", cascade="all, delete-orphan")
    pull_request = relationship("PullRequest", back_populates="task", uselist=False, cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_task_organization_project", "organization", "project"),
    )
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with nested relationships"""
        result = super().dict()
        
        # Add nested repository
        if self.repository:
            result["repository"] = {
                "id": str(self.repository.id),
                "name": self.repository.name,
                "url": self.repository.url,
            }
            
        # Add nested pull request
        if self.pull_request:
            result["pull_request"] = {
                "id": str(self.pull_request.id),
                "title": self.pull_request.title,
                "status": self.pull_request.status,
                "url": self.pull_request.url,
            }
            
        # Don't include code generations by default (could be many)
        return result