"""
Pydantic schemas for the Health Score API.

This module contains all the Pydantic models used for request/response validation
and serialization throughout the application.
"""
from .base import BaseSchema, IDSchemaMixin, TimestampSchema
from .health_schemas import (
    HealthMetricType,
    HealthMetricAggregation,
    HealthMetricBase,
    HealthMetricCreate,
    HealthMetricUpdate,
    HealthMetricInDBBase,
    HealthMetricResponse,
    HealthMetricListResponse,
    HealthMetricAggregationResponse,
    HealthMetricTrendResponse,
)

# Re-export all schemas for easier imports
__all__ = [
    # Base schemas
    "BaseSchema",
    "IDSchemaMixin",
    "TimestampSchema",
    
    # Health metric schemas
    "HealthMetricType",
    "HealthMetricAggregation",
    "HealthMetricBase",
    "HealthMetricCreate",
    "HealthMetricUpdate",
    "HealthMetricInDBBase",
    "HealthMetricResponse",
    "HealthMetricListResponse",
    "HealthMetricAggregationResponse",
    "HealthMetricTrendResponse",
]
