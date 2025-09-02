from datetime import datetime
from typing import Any, Dict, Optional, TypeVar, Generic, Type
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# Type variable for generic schema types
T = TypeVar('T')

class BaseSchema(BaseModel):
    """
    Base schema with common fields and configuration.
    All API schemas should inherit from this class.
    """
    model_config = {
        # Allow population by field name (e.g., convert from snake_case to camelCase)
        "populate_by_name": True,

        # Use enum values instead of enum objects
        "use_enum_values": True,

        # Allow arbitrary types for fields that might have custom types
        "arbitrary_types_allowed": True,

        # Enable from_attributes for compatibility with SQLAlchemy models
        "from_attributes": True,

        # Example schema for OpenAPI documentation
        "json_schema_extra": {
            "example": {
                "id": 1,
                "created_at": "2025-09-02T00:00:00Z",
                "updated_at": "2025-09-02T00:00:00Z"
            }
        }
    }

class TimestampSchema(BaseSchema):
    """
    Schema with timestamp fields for creation and updates.
    """
    created_at: Optional[datetime] = Field(
        None, 
        description="Timestamp when the record was created",
        example="2023-01-01T00:00:00Z"
    )
    updated_at: Optional[datetime] = Field(
        None, 
        description="Timestamp when the record was last updated",
        example="2023-01-01T00:00:00Z"
    )

class IDSchema(BaseSchema):
    """
    Schema with a single ID field.
    """
    id: int = Field(..., description="Unique identifier", example=1)

class IDSchemaMixin(BaseSchema):
    """
    Mixin class that adds an ID field to a schema.
    """
    id: int = Field(..., description="Unique identifier", example=1)

class ListResponse(BaseModel, Generic[T]):
    """
    Generic list response schema for paginated results.
    """
    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items", ge=0)
    page: int = Field(1, description="Current page number", ge=1)
    pages: int = Field(..., description="Total number of pages", ge=1)
    size: int = Field(..., description="Number of items per page", ge=1, le=100)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "pages": 1,
                "size": 10
            }
        }


class MessageResponse(BaseSchema):
    """
    Standard message response schema for API responses.
    """
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully"
            }
        }


class ErrorResponse(BaseSchema):
    """
    Standard error response schema for API error responses.
    """
    error: str = Field(..., description="Error message")
    code: Optional[int] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional error details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Resource not found",
                "code": 404,
                "details": {"resource": "user", "id": 123}
            }
        }


class PaginationParams(BaseModel):
    """
    Query parameters for pagination.
    """
    page: int = Field(1, description="Page number", ge=1)
    size: int = Field(10, description="Items per page", ge=1, le=100)

    @field_validator('size')
    def validate_page_size(cls, v):
        if v > 100:
            raise ValueError("Page size cannot exceed 100")
        return v


class SortOrder(str, Enum):
    """Sort order for query parameters"""
    ASC = "asc"
    DESC = "desc"


class SortParams(BaseModel):
    """
    Query parameters for sorting results.
    """
    sort_by: Optional[str] = Field(
        None, 
        description="Field to sort by (default depends on endpoint)"
    )
    order: SortOrder = Field(
        SortOrder.ASC, 
        description="Sort order (asc or desc)"
    )


class SearchParams(BaseModel):
    """
    Query parameters for search functionality.
    """
    query: Optional[str] = Field(
        None, 
        description="Search query string",
        min_length=1,
        max_length=100
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "morning run"
            }
        }
