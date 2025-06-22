"""
Pydantic models for health metrics API.
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, Field, validator, confloat, conint

from .base import BaseSchema, IDSchemaMixin, TimestampSchema

class HealthMetricType(str, Enum):
    """Types of health metrics that can be tracked."""
    # Vital Signs
    HEART_RATE = "heart_rate"  # BPM
    BLOOD_PRESSURE_SYSTOLIC = "blood_pressure_systolic"  # mmHg
    BLOOD_PRESSURE_DIASTOLIC = "blood_pressure_diastolic"  # mmHg
    BLOOD_OXYGEN = "blood_oxygen"  # SpO2 %
    BODY_TEMPERATURE = "body_temperature"  # °C
    RESPIRATORY_RATE = "respiratory_rate"  # breaths per minute

    # Body Composition
    WEIGHT = "weight"  # kg
    HEIGHT = "height"  # cm
    BMI = "bmi"  # kg/m²
    BODY_FAT_PERCENTAGE = "body_fat_percentage"  # %
    MUSCLE_MASS = "muscle_mass"  # kg
    BONE_MASS = "bone_mass"  # kg
    WATER_PERCENTAGE = "water_percentage"  # %

    # Blood Tests
    FASTING_GLUCOSE = "fasting_glucose"  # mg/dL
    HBA1C = "hba1c"  # %
    TOTAL_CHOLESTEROL = "total_cholesterol"  # mg/dL
    HDL_CHOLESTEROL = "hdl_cholesterol"  # mg/dL
    LDL_CHOLESTEROL = "ldl_cholesterol"  # mg/dL
    TRIGLYCERIDES = "triglycerides"  # mg/dL

    # Activity and Fitness
    STEPS = "steps"  # count
    ACTIVE_MINUTES = "active_minutes"  # minutes
    EXERCISE_MINUTES = "exercise_minutes"  # minutes
    CALORIES_BURNED = "calories_burned"  # kcal
    RESTING_HEART_RATE = "resting_heart_rate"  # BPM
    VO2_MAX = "vo2_max"  # mL/kg/min

    # Sleep
    SLEEP_DURATION = "sleep_duration"  # minutes
    SLEEP_EFFICIENCY = "sleep_efficiency"  # %
    DEEP_SLEEP_DURATION = "deep_sleep_duration"  # minutes
    REM_SLEEP_DURATION = "rem_sleep_duration"  # minutes
    SLEEP_SCORE = "sleep_score"  # 0-100

    # Nutrition
    CALORIES_CONSUMED = "calories_consumed"  # kcal
    PROTEIN_INTAKE = "protein_intake"  # g
    CARBS_INTAKE = "carbs_intake"  # g
    FAT_INTAKE = "fat_intake"  # g
    FIBER_INTAKE = "fiber_intake"  # g
    SUGAR_INTAKE = "sugar_intake"  # g
    WATER_INTAKE = "water_intake"  # mL

    # Mental Wellbeing
    STRESS_LEVEL = "stress_level"  # 1-10
    MOOD_LEVEL = "mood_level"  # 1-10
    ENERGY_LEVEL = "energy_level"  # 1-10


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
    user_id: Optional[int] = Field(None, description="User ID (automatically set from auth token)")


class HealthMetricUpdate(BaseModel):
    """Schema for updating an existing health metric."""
    value: Optional[Union[float, int]] = Field(None, description="Updated numeric value")
    unit: Optional[str] = Field(None, description="Updated unit of measurement")
    recorded_at: Optional[datetime] = Field(None, description="Updated timestamp")
    notes: Optional[str] = Field(None, description="Updated notes")
    source: Optional[str] = Field(None, description="Updated source")


class HealthMetricInDBBase(HealthMetricBase, IDSchemaMixin, TimestampSchema):
    """Base schema for health metrics stored in the database."""
    user_id: int = Field(..., description="ID of the user who owns this metric")

    class Config:
        from_attributes = True


class HealthMetricResponse(HealthMetricInDBBase):
    """Schema for health metric responses."""
    pass


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
