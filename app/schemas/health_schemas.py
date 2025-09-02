"""
Pydantic models for health metrics API.
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, Field, ConfigDict, validator, confloat, conint, model_serializer, model_validator

from .base import BaseSchema, IDSchemaMixin, TimestampSchema
from app.domain.enums import HealthMetricType


class HealthMetricAggregation(str, Enum):
    """Aggregation levels for health metrics."""
    DAILY = "day"
    WEEKLY = "week"
    MONTHLY = "month"
    YEARLY = "year"


class HealthMetricBase(BaseSchema):
    """Base schema for health metrics."""
    metric_type: HealthMetricType = Field(..., description="Type of health metric")
    value: Union[float, int] = Field(..., description="Numeric value of the metric")
    unit: str = Field(..., description="Unit of measurement (e.g., bpm, mmHg, kg)")
    recorded_at: datetime = Field(default_factory=datetime.utcnow, description="When the measurement was taken")
    notes: Optional[str] = Field(None, description="Additional notes about the measurement")
    source: Optional[str] = Field("user", description="Source of the measurement (e.g., 'device', 'manual')")


class HealthMetricCreate(HealthMetricBase):
    """Schema for creating a new health metric."""
    systolic: Optional[int] = Field(None, ge=40, le=300, description="Systolic (mmHg) for blood pressure")
    diastolic: Optional[int] = Field(None, ge=30, le=200, description="Diastolic (mmHg) for blood pressure")

    @model_validator(mode="before")
    @classmethod
    def normalize_bp(cls, data: Any):
        if isinstance(data, dict):
            mt = data.get("metric_type")
            if mt == HealthMetricType.BLOOD_PRESSURE:
                sys = data.get("systolic")
                dia = data.get("diastolic")
                if sys is None or dia is None:
                    raise ValueError("For blood_pressure you must provide both 'systolic' and 'diastolic'.")
                data.setdefault("unit", "mmHg")
                data["value"] = 0.0
        return data

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "metric_type": "heart_rate",
            "value": 75,
            "systolic": 120,
            "diastolic": 80,
            "unit": "bpm",
            "recorded_at": "2025-08-28T21:03:00Z",
            "source": "device",
            "notes": "evening check"
        }
    })


class HealthMetricUpdate(BaseModel):
    """Schema for updating an existing health metric."""
    value: Optional[Union[float, int]] = Field(
        None, description="New numeric value for non-blood_pressure metrics"
    )

    systolic: Optional[int] = Field(None, ge=40, le=300, description="Systolic (mmHg) for blood pressure")
    diastolic: Optional[int] = Field(None, ge=30, le=200, description="Diastolic (mmHg) for blood pressure")

    unit: Optional[str] = Field(None, description="Updated unit of measurement")
    recorded_at: Optional[datetime] = Field(None, description="Updated timestamp")
    notes: Optional[str] = Field(None, description="Updated notes")
    source: Optional[str] = Field(None, description="Updated source")


class HealthMetricInDBBase(HealthMetricBase, IDSchemaMixin, TimestampSchema):
    """Base schema for health metrics stored in the database."""
    user_id: int
    raw_data: Optional[Dict[str, Any]] = Field(None, exclude=True)
    model_config = ConfigDict(from_attributes=True)

class HealthMetricResponse(HealthMetricInDBBase):
    """Schema for health metric responses."""
    value: Union[float, int, str, None] = Field(None)

    @model_serializer(mode="wrap")
    def _serialize(self, handler):
        data = handler(self)
        if self.metric_type == HealthMetricType.BLOOD_PRESSURE and self.raw_data:
            sys = self.raw_data.get("systolic")
            dia = self.raw_data.get("diastolic")
            if sys is not None and dia is not None:
                data["value"] = f"{int(sys)}/{int(dia)}"
        return data


class HealthMetricListResponse(BaseModel):
    """Schema for paginated list of health metrics."""
    total: int = Field(..., description="Total number of items")
    items: List[HealthMetricResponse] = Field(..., description="List of health metrics")


class HealthMetricAggregationResponse(BaseModel):
    """Schema for aggregated health metrics response."""
    metric_type: HealthMetricType = Field(..., description="Type of health metric")
    aggregation: HealthMetricAggregation = Field(..., description="Aggregation level")
    data: List[Dict[str, Any]] = Field(..., description="Aggregated data points")


class HealthMetricTrendResponse(BaseModel):
    """Schema for health metric trend data."""
    current_value: Optional[float] = Field(None, description="Most recent value")
    current_unit: Optional[str] = Field(None, description="Unit of the current value")
    change_percent: Optional[float] = Field(None, description="Percentage change from previous period")
    trend: str = Field(..., description="Trend direction: 'up', 'down', or 'neutral'")
    data_points: List[Dict[str, Any]] = Field(..., description="Historical data points")


# Update __all__ in __init__.py to include these schemas
__all__ = [
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
