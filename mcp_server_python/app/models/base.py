"""
Base SQLAlchemy models for the MCP server
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar

from sqlalchemy import Column, DateTime, MetaData, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr

# SQLAlchemy naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

# Type variable for base model instances
ModelType = TypeVar("ModelType", bound="Base")


@as_declarative(metadata=metadata)
class Base:
    """Base class for all SQLAlchemy models"""
    
    # Generate __tablename__ automatically from class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Common columns for all models
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    def dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        
        Returns:
            Dictionary representation of the model
        """
        result = {}
        for key in self.__mapper__.c.keys():
            value = getattr(self, key)
            if isinstance(value, uuid.UUID):
                value = str(value)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[key] = value
        return result