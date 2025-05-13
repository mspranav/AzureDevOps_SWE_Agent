"""
Repository model definition
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Index, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Repository(Base):
    """Repository model"""
    
    # Columns
    url = Column(String, nullable=False, unique=True, comment="Repository URL")
    name = Column(String, nullable=False, comment="Repository name")
    organization = Column(String, nullable=False, comment="Azure DevOps organization")
    project = Column(String, nullable=False, comment="Azure DevOps project")
    repository_id = Column(String, nullable=False, comment="Repository ID in Azure DevOps")
    default_branch = Column(String, nullable=False, default="main", comment="Default branch name")
    analysis = Column(String, nullable=False, default="{}", comment="Repository analysis results")
    languages = Column(String, nullable=False, default="{}", comment="Detected languages and their percentages")
    frameworks = Column(String, nullable=False, default="{}", comment="Detected frameworks")
    code_style = Column(String, nullable=False, default="{}", comment="Detected code style preferences")
    last_analyzed_at = Column(DateTime, nullable=True, comment="When the repository was last analyzed")
    last_cloned_at = Column(DateTime, nullable=True, comment="When the repository was last cloned")
    metadata = Column(String, nullable=False, default="{}", comment="Additional metadata for the repository")
    
    # Relationships
    tasks = relationship("Task", back_populates="repository")
    pull_requests = relationship("PullRequest", back_populates="repository")
    
    # Indexes
    __table_args__ = (
        Index("ix_repository_organization_project_repository_id", 
              "organization", "project", "repository_id", unique=True),
    )
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with calculated properties"""
        import json
        result = super().dict()
        
        # Parse JSON strings to dictionaries
        for json_field in ["analysis", "languages", "frameworks", "code_style", "metadata"]:
            try:
                result[json_field] = json.loads(result[json_field])
            except (TypeError, json.JSONDecodeError):
                result[json_field] = {}
        
        # Add language summary
        if result["languages"]:
            primary_language = max(result["languages"].items(), key=lambda x: x[1])[0] if result["languages"] else None
            result["primary_language"] = primary_language
            
        # Add framework summary
        if result["frameworks"]:
            result["primary_frameworks"] = list(result["frameworks"].keys())[:3] if result["frameworks"] else []
            
        # Don't include tasks or PRs by default (could be many)
        return result