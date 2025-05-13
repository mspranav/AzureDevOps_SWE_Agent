"""
CodeGeneration model definition
"""

import enum
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class CodeGenerationStatus(str, enum.Enum):
    """Code generation status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class CodeGenerationAction(str, enum.Enum):
    """Code generation action enum"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"


class CodeGeneration(Base):
    """CodeGeneration model"""
    
    # Columns
    task_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("task.id"), 
        nullable=False,
        index=True,
        comment="ID of the associated task"
    )
    language = Column(String, nullable=False, index=True, comment="Programming language")
    framework = Column(String, nullable=True, comment="Framework used")
    file_path = Column(String, nullable=False, comment="Path to the file being generated/modified")
    action = Column(
        Enum(CodeGenerationAction),
        nullable=False,
        default=CodeGenerationAction.CREATE,
        comment="Action being performed on the file"
    )
    requirements = Column(JSONB, nullable=False, default={}, comment="Requirements for code generation")
    original_code = Column(Text, nullable=True, comment="Original code before modification (for modify action)")
    generated_code = Column(Text, nullable=True, comment="Generated code implementation")
    test_code = Column(Text, nullable=True, comment="Generated test code (if applicable)")
    prompt = Column(Text, nullable=True, comment="Prompt used for code generation")
    model_name = Column(String, nullable=True, comment="AI model name used for generation")
    model_version = Column(String, nullable=True, comment="AI model version used for generation")
    status = Column(
        Enum(CodeGenerationStatus),
        nullable=False,
        default=CodeGenerationStatus.PENDING,
        index=True,
        comment="Status of code generation"
    )
    error = Column(Text, nullable=True, comment="Error message if code generation failed")
    metrics = Column(JSONB, nullable=False, default={}, comment="Generation metrics (tokens, time, etc.)")
    metadata = Column(JSONB, nullable=False, default={}, comment="Additional metadata for code generation")
    
    # Relationships
    task = relationship("Task", back_populates="code_generations")
    
    def dict(self, include_code: bool = False) -> Dict[str, Any]:
        """
        Convert model to dictionary
        
        Args:
            include_code: Whether to include code contents (can be large)
            
        Returns:
            Dictionary representation
        """
        result = super().dict()
        
        # Optionally exclude code contents
        if not include_code:
            result.pop("original_code", None)
            result.pop("generated_code", None)
            result.pop("test_code", None)
            result.pop("prompt", None)
            
        return result