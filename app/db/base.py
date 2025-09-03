from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, DateTime, func
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

class CustomBase:
    """Base class for all database models with common functionality."""
    
    # Auto-generated fields
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Table naming convention (optional)
    @declared_attr
    def __tablename__(cls) -> str:
        ""
        Generate __tablename__ automatically based on class name.
        Converts CamelCase to snake_case and appends 's' for pluralization.
        Example: 'UserActivity' -> 'user_activities'
        """
        import re
        # Convert CamelCase to snake_case
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        # Handle special cases for pluralization
        if name.endswith('y'):
            return f"{name[:-1]}ies"
        elif name.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return f"{name}es"
        else:
            return f"{name}s"
    
    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary, excluding private attributes and relationships.
        
        Args:
            exclude: List of field names to exclude from the result
            
        Returns:
            Dictionary representation of the model
        """
        if exclude is None:
            exclude = []
            
        result = {}
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
                
            value = getattr(self, column.name)
            
            # Handle datetime objects
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            
            result[column.name] = value
            
        return result
    
    def update(self, **kwargs) -> None:
        """
        Update model attributes.
        
        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

# Create the declarative base with our custom functionality
Base = declarative_base(cls=CustomBase)
