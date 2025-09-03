from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator, conint, confloat, HttpUrl
from pydantic.types import PositiveInt, PositiveFloat

from .base import BaseSchema, TimestampSchema, IDSchemaMixin

# Enums for health metrics and categories
class HealthMetricType(str, Enum):
    """Types of health metrics that can be tracked"""
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
    
    # Custom Metrics
    CUSTOM = "custom"

class HealthMetricCategory(str, Enum):
    """Categories for grouping health metrics"""
    VITALS = "vitals"
    BODY_COMPOSITION = "body_composition"
    BLOOD_TESTS = "blood_tests"
    ACTIVITY = "activity"
    SLEEP = "sleep"
    NUTRITION = "nutrition"
    MENTAL_WELLBEING = "mental_wellbeing"
    CUSTOM = "custom"

class HealthMetricUnit(str, Enum):
    """Standard units for health metrics"""
    # Common units
    COUNT = "count"
    PERCENT = "%"
    BPM = "bpm"  # beats per minute
    MMHG = "mmHg"  # millimeters of mercury
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    KILOGRAMS = "kg"
    GRAMS = "g"
    POUNDS = "lb"
    CENTIMETERS = "cm"
    METERS = "m"
    INCHES = "in"
    FEET = "ft"
    MILLILITERS = "mL"
    LITERS = "L"
    OUNCES = "oz"
    CALORIES = "kcal"
    KILOMETERS = "km"
    MILES = "mi"
    MINUTES = "minutes"
    HOURS = "hours"
    ML_KG_MIN = "mL/kg/min"  # VO2 max
    MG_DL = "mg/dL"  # blood glucose, cholesterol
    MMOL_L = "mmol/L"  # alternative blood glucose, cholesterol
    
    # Custom/derived units
    SCORE = "score"  # for scores (e.g., sleep score)
    LEVEL = "level"  # for subjective levels (e.g., stress, mood)
    CUSTOM = "custom"  # for custom units

class HealthMetricTrend(str, Enum):
    """Trend direction for health metrics"""
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"
    FLUCTUATING = "fluctuating"
    UNKNOWN = "unknown"

class HealthScoreCategory(str, Enum):
    """Categories for health scores"""
    OVERALL = "overall"
    CARDIOVASCULAR = "cardiovascular"
    METABOLIC = "metabolic"
    RESPIRATORY = "respiratory"
    MENTAL = "mental"
    FITNESS = "fitness"
    NUTRITION = "nutrition"
    SLEEP = "sleep"
    LONGEVITY = "longevity"
    CUSTOM = "custom"

class GoalStatus(str, Enum):
    """Status of a health goal"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"

class GoalFrequency(str, Enum):
    """Frequency for goal tracking"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

# Base Schemas
class HealthMetricBase(BaseSchema):
    """Base schema for health metrics"""
    metric_type: HealthMetricType = Field(..., description="Type of health metric")
    category: HealthMetricCategory = Field(..., description="Category of the metric")
    value: float = Field(..., description="Numeric value of the metric")
    unit: HealthMetricUnit = Field(..., description="Unit of measurement")
    
    # Optional fields
    source: Optional[str] = Field(None, description="Source of the measurement (e.g., device name, manual)")
    notes: Optional[str] = Field(None, description="Additional notes about the measurement")
    is_manual_entry: bool = Field(False, description="Whether the value was entered manually")
    
    # Metadata
    measured_at: datetime = Field(..., description="When the measurement was taken")
    timezone: str = Field("UTC", description="Timezone where the measurement was taken")
    
    # Confidence/accuracy
    confidence_score: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Confidence score (0-1) for the measurement accuracy"
    )
    
    # Raw data or additional details
    raw_data: Optional[Dict[str, Any]] = Field(
        None, 
        description="Raw data or additional details about the measurement"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "metric_type": "heart_rate",
                "category": "vitals",
                "value": 72.5,
                "unit": "bpm",
                "source": "Apple Watch",
                "notes": "Measured after 5 minutes of rest",
                "is_manual_entry": False,
                "measured_at": "2023-06-07T14:30:00Z",
                "timezone": "America/New_York",
                "confidence_score": 0.95,
                "raw_data": {
                    "device_id": "aw-12345",
                    "measurement_context": "resting"
                }
            }
        }

class HealthMetricCreate(HealthMetricBase):
    """Schema for creating a new health metric"""
    user_id: Optional[int] = Field(None, description="User ID (defaults to current user)")

class HealthMetricUpdate(BaseModel):
    """Schema for updating an existing health metric"""
    value: Optional[float] = None
    unit: Optional[HealthMetricUnit] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    raw_data: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "value": 71.0,
                "notes": "Updated after recalibration",
                "confidence_score": 0.98
            }
        }

class HealthMetricResponse(HealthMetricBase, IDSchemaMixin, TimestampSchema):
    """Schema for health metric response"""
    user_id: int = Field(..., description="User who owns this metric")
    trend: Optional[HealthMetricTrend] = Field(
        None, 
        description="Trend direction based on previous measurements"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "user_id": 456,
                "metric_type": "heart_rate",
                "category": "vitals",
                "value": 72.5,
                "unit": "bpm",
                "source": "Apple Watch",
                "measured_at": "2023-06-07T14:30:00Z",
                "created_at": "2023-06-07T14:31:22Z",
                "updated_at": "2023-06-07T14:31:22Z",
                "trend": "stable"
            }
        }

# Health Score Schemas
class HealthScoreBase(BaseSchema):
    """Base schema for health scores"""
    category: HealthScoreCategory = Field(..., description="Category of the health score")
    score: float = Field(..., ge=0, le=100, description="Health score (0-100)")
    
    # Optional fields
    confidence_score: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Confidence score (0-1) for the calculated score"
    )
    contributing_metrics: Optional[Dict[str, float]] = Field(
        None, 
        description="Metrics that contributed to this score with their weights"
    )
    insights: Optional[List[str]] = Field(
        None, 
        description="Insights or observations about the score"
    )
    recommendations: Optional[List[str]] = Field(
        None, 
        description="Recommended actions to improve the score"
    )
    
    # Metadata
    calculated_at: datetime = Field(..., description="When the score was calculated")
    timezone: str = Field("UTC", description="Timezone for the calculation")
    
    class Config:
        schema_extra = {
            "example": {
                "category": "overall",
                "score": 78.5,
                "confidence_score": 0.92,
                "contributing_metrics": {
                    "resting_heart_rate": 0.3,
                    "sleep_score": 0.25,
                    "activity_level": 0.25,
                    "nutrition_score": 0.2
                },
                "insights": [
                    "Your overall health is good, but could be improved with better sleep quality.",
                    "Your activity level is above average for your age group."
                ],
                "recommendations": [
                    "Aim for 7-9 hours of sleep per night.",
                    "Consider adding strength training 2-3 times per week."
                ],
                "calculated_at": "2023-06-07T00:00:00Z",
                "timezone": "America/New_York"
            }
        }

class HealthScoreCreate(HealthScoreBase):
    """Schema for creating a new health score"""
    user_id: Optional[int] = Field(None, description="User ID (defaults to current user)")

class HealthScoreUpdate(BaseModel):
    """Schema for updating an existing health score"""
    score: Optional[float] = Field(None, ge=0, le=100)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "score": 80.2,
                "insights": ["Updated with latest sleep data"],
                "recommendations": ["Consider a sleep study if sleep issues persist"]
            }
        }

class HealthScoreResponse(HealthScoreBase, IDSchemaMixin, TimestampSchema):
    """Schema for health score response"""
    user_id: int = Field(..., description="User who owns this score")
    trend: Optional[HealthMetricTrend] = Field(
        None, 
        description="Trend direction compared to previous scores"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id": 789,
                "user_id": 456,
                "category": "overall",
                "score": 78.5,
                "calculated_at": "2023-06-07T00:00:00Z",
                "created_at": "2023-06-07T00:05:12Z",
                "updated_at": "2023-06-07T00:05:12Z",
                "trend": "improving"
            }
        }

# Health Goal Schemas
class HealthGoalBase(BaseSchema):
    """Base schema for health goals"""
    title: str = Field(..., max_length=100, description="Short title of the goal")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description")
    
    # Target metrics
    target_metric: HealthMetricType = Field(..., description="Metric being tracked")
    target_value: float = Field(..., description="Target value to achieve")
    current_value: Optional[float] = Field(None, description="Current value of the metric")
    initial_value: Optional[float] = Field(None, description="Value when the goal was created")
    unit: HealthMetricUnit = Field(..., description="Unit of measurement")
    
    # Timeframe
    start_date: date = Field(..., description="When the goal period starts")
    end_date: Optional[date] = Field(None, description="Target completion date (optional)")
    frequency: Optional[GoalFrequency] = Field(
        None, 
        description="How often the goal should be measured/achieved"
    )
    
    # Progress tracking
    status: GoalStatus = Field(GoalStatus.NOT_STARTED, description="Current status of the goal")
    progress_percentage: float = Field(
        0.0, 
        ge=0, 
        le=100, 
        description="Progress percentage (0-100)"
    )
    
    # Motivation and tracking
    motivation: Optional[str] = Field(None, description="Reason or motivation for the goal")
    is_public: bool = Field(False, description="Whether the goal is visible to others")
    
    # Reminders and notifications
    reminder_enabled: bool = Field(False, description="Whether reminders are enabled")
    reminder_days: Optional[List[str]] = Field(
        None, 
        description="Days of the week to send reminders (e.g., ['mon', 'wed', 'fri'])"
    )
    reminder_time: Optional[str] = Field(
        None, 
        description="Time of day to send reminders (e.g., '19:00')",
        regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    )
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Lose 5kg in 3 months",
                "description": "Gradual weight loss through diet and exercise",
                "target_metric": "weight",
                "target_value": 70.0,
                "current_value": 75.0,
                "initial_value": 75.0,
                "unit": "kg",
                "start_date": "2023-06-01",
                "end_date": "2023-08-31",
                "frequency": "weekly",
                "status": "in_progress",
                "progress_percentage": 30.0,
                "motivation": "Improve overall health and fitness",
                "is_public": False,
                "reminder_enabled": True,
                "reminder_days": ["mon", "wed", "fri"],
                "reminder_time": "19:00"
            }
        }
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v:
            if v < values['start_date']:
                raise ValueError("End date must be after start date")
        return v

class HealthGoalCreate(HealthGoalBase):
    """Schema for creating a new health goal"""
    user_id: Optional[int] = Field(None, description="User ID (defaults to current user)")

class HealthGoalUpdate(BaseModel):
    """Schema for updating an existing health goal"""
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    status: Optional[GoalStatus] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    is_public: Optional[bool] = None
    reminder_enabled: Optional[bool] = None
    reminder_days: Optional[List[str]] = None
    reminder_time: Optional[str] = Field(
        None, 
        regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    )
    
    class Config:
        schema_extra = {
            "example": {
                "current_value": 73.5,
                "progress_percentage": 60.0,
                "status": "in_progress",
                "reminder_enabled": True
            }
        }

class HealthGoalResponse(HealthGoalBase, IDSchemaMixin, TimestampSchema):
    """Schema for health goal response"""
    user_id: int = Field(..., description="User who owns this goal")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 101,
                "user_id": 456,
                "title": "Lose 5kg in 3 months",
                "target_metric": "weight",
                "target_value": 70.0,
                "current_value": 73.5,
                "unit": "kg",
                "status": "in_progress",
                "progress_percentage": 60.0,
                "created_at": "2023-06-01T10:00:00Z",
                "updated_at": "2023-07-15T14:30:00Z"
            }
        }

# Health Insights and Analytics
class HealthInsight(BaseModel):
    """Schema for health insights and analytics"""
    id: str = Field(..., description="Unique identifier for the insight")
    title: str = Field(..., description="Short title of the insight")
    description: str = Field(..., description="Detailed description of the insight")
    category: HealthScoreCategory = Field(..., description="Category of the insight")
    impact: Literal["high", "medium", "low"] = Field(..., description="Impact level of the insight")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    related_metrics: List[Dict[str, Any]] = Field(
        ..., 
        description="Metrics that contributed to this insight"
    )
    recommendations: List[str] = Field(..., description="Recommended actions")
    generated_at: datetime = Field(..., description="When the insight was generated")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "insight_123",
                "title": "Improved Sleep Correlates with Lower Resting Heart Rate",
                "description": "Your average resting heart rate decreased by 5 bpm on days when you got 7+ hours of sleep.",
                "category": "sleep",
                "impact": "medium",
                "confidence": 0.85,
                "related_metrics": [
                    {"metric": "sleep_duration", "value": "7.5h", "trend": "improving"},
                    {"metric": "resting_heart_rate", "value": "62 bpm", "trend": "decreasing"}
                ],
                "recommendations": [
                    "Aim for at least 7 hours of sleep per night",
                    "Maintain a consistent sleep schedule"
                ],
                "generated_at": "2023-06-07T12:00:00Z"
            }
        }

class HealthSummary(BaseModel):
    """Schema for a comprehensive health summary"""
    user_id: int = Field(..., description="User ID")
    date: date = Field(..., description="Date of the summary")
    
    # Overview
    overall_score: float = Field(..., ge=0, le=100, description="Overall health score (0-100)")
    score_trend: HealthMetricTrend = Field(..., description="Trend of the overall score")
    
    # Category scores
    category_scores: Dict[HealthScoreCategory, float] = Field(
        ..., 
        description="Scores for each health category"
    )
    
    # Daily metrics
    daily_metrics: Dict[str, Any] = Field(
        ..., 
        description="Key metrics for the day"
    )
    
    # Highlights and lowlights
    highlights: List[str] = Field(..., description="Positive highlights")
    areas_for_improvement: List[str] = Field(..., description="Areas needing attention")
    
    # Insights and recommendations
    top_insights: List[HealthInsight] = Field(..., description="Key health insights")
    priority_recommendations: List[str] = Field(..., description="Top recommendations")
    
    # Generated at timestamp
    generated_at: datetime = Field(..., description="When the summary was generated")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 456,
                "date": "2023-06-07",
                "overall_score": 78.5,
                "score_trend": "improving",
                "category_scores": {
                    "overall": 78.5,
                    "cardiovascular": 85.0,
                    "metabolic": 72.0,
                    "fitness": 75.0,
                    "sleep": 65.0,
                    "nutrition": 82.0,
                    "mental": 80.0
                },
                "daily_metrics": {
                    "steps": 8452,
                    "active_minutes": 45,
                    "sleep_duration": 6.5,
                    "water_intake_ml": 2200,
                    "calories_burned": 2450,
                    "calories_consumed": 2100
                },
                "highlights": [
                    "Great job on meeting your step goal 5 days this week!",
                    "Your resting heart rate has decreased by 3 bpm this month."
                ],
                "areas_for_improvement": [
                    "Aim for 7-9 hours of sleep per night (averaging 6.5h this week).",
                    "Consider adding more protein to your breakfast meals."
                ],
                "priority_recommendations": [
                    "Try going to bed 30 minutes earlier to improve sleep duration.",
                    "Add a protein source like eggs or Greek yogurt to your breakfast.",
                    "Schedule a 10-minute walk after lunch to increase daily activity."
                ],
                "generated_at": "2023-06-07T08:00:00Z"
            }
        }
