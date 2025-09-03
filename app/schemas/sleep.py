from datetime import date, datetime, time
from enum import Enum, auto
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, conint, confloat

from .base import BaseSchema, TimestampSchema, IDSchemaMixin

# Enums for sleep tracking
class SleepStageType(str, Enum):
    """Types of sleep stages"""
    AWAKE = "awake"
    LIGHT = "light"
    DEEP = "deep"
    REM = "rem"
    OUT_OF_BED = "out_of_bed"
    UNMEASURABLE = "unmeasurable"

class SleepQualityRating(int, Enum):
    """Subjective sleep quality ratings"""
    VERY_POOR = 1
    POOR = 2
    FAIR = 3
    GOOD = 4
    EXCELLENT = 5

class SleepDisruptionCause(str, Enum):
    """Common causes of sleep disruptions"""
    NOISE = "noise"
    LIGHT = "light"
    TEMPERATURE = "temperature"
    PAIN = "pain"
    BATHROOM = "bathroom"
    DREAM = "dream"
    UNKNOWN = "unknown"
    OTHER = "other"

# Base Schemas
class SleepStage(BaseModel):
    """Schema for a single sleep stage period"""
    stage: SleepStageType = Field(..., description="Type of sleep stage")
    start_time: datetime = Field(..., description="When the stage began")
    end_time: datetime = Field(..., description="When the stage ended")
    duration_seconds: int = Field(..., ge=0, description="Duration in seconds")
    
    @validator('end_time')
    def validate_times(cls, v, values):
        if 'start_time' in values and v < values['start_time']:
            raise ValueError("end_time must be after start_time")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "stage": "deep",
                "start_time": "2023-06-07T22:15:00Z",
                "end_time": "2023-06-07T23:45:00Z",
                "duration_seconds": 5400
            }
        }

class SleepDisruption(BaseModel):
    """Schema for sleep disruptions during the night"""
    start_time: datetime = Field(..., description="When the disruption began")
    end_time: datetime = Field(..., description="When the disruption ended")
    duration_seconds: int = Field(..., ge=0, description="Duration in seconds")
    cause: SleepDisruptionCause = Field(..., description="Cause of the disruption")
    notes: Optional[str] = Field(None, description="Additional notes about the disruption")
    
    @validator('end_time')
    def validate_times(cls, v, values):
        if 'start_time' in values and v < values['start_time']:
            raise ValueError("end_time must be after start_time")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "start_time": "2023-06-08T02:30:00Z",
                "end_time": "2023-06-08T02:45:00Z",
                "duration_seconds": 900,
                "cause": "bathroom",
                "notes": "Woke up to use the bathroom"
            }
        }

class SleepRecordBase(BaseSchema):
    """Base schema for sleep records"""
    # Timing
    sleep_start: datetime = Field(..., description="When the sleep period began")
    sleep_end: datetime = Field(..., description="When the sleep period ended")
    timezone: str = Field("UTC", description="Timezone where sleep occurred")
    
    # Sleep stages and metrics
    stages: List[SleepStage] = Field(..., description="Sleep stages during the night")
    total_sleep_seconds: int = Field(..., ge=0, description="Total time asleep in seconds")
    awake_seconds: int = Field(..., ge=0, description="Total time awake in bed in seconds")
    light_sleep_seconds: int = Field(..., ge=0, description="Time in light sleep in seconds")
    deep_sleep_seconds: int = Field(..., ge=0, description="Time in deep sleep in seconds")
    rem_sleep_seconds: int = Field(..., ge=0, description="Time in REM sleep in seconds")
    
    # Sleep quality metrics
    sleep_efficiency: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Percentage of time in bed spent sleeping"
    )
    sleep_latency_seconds: Optional[int] = Field(
        None, 
        ge=0, 
        description="Time taken to fall asleep in seconds"
    )
    wake_after_sleep_onset_seconds: Optional[int] = Field(
        None, 
        ge=0, 
        description="Time spent awake after initially falling asleep"
    )
    
    # Disruptions and movements
    disruptions: List[SleepDisruption] = Field(
        default_factory=list, 
        description="Significant disruptions during sleep"
    )
    movement_count: Optional[int] = Field(
        None, 
        ge=0, 
        description="Number of significant movements during sleep"
    )
    
    # Subjective measures
    quality_rating: Optional[SleepQualityRating] = Field(
        None, 
        description="User's subjective rating of sleep quality"
    )
    rested_rating: Optional[int] = Field(
        None, 
        ge=1, 
        le=10, 
        description="How rested the user feels (1-10)"
    )
    
    # Environmental factors
    room_temperature_c: Optional[float] = Field(
        None, 
        description="Room temperature in Celsius"
    )
    noise_level_db: Optional[float] = Field(
        None, 
        ge=0, 
        description="Average noise level in decibels"
    )
    light_level_lux: Optional[float] = Field(
        None, 
        ge=0, 
        description="Average light level in lux"
    )
    
    # Additional metadata
    notes: Optional[str] = Field(None, description="Additional notes about the sleep")
    source: Optional[str] = Field(
        None, 
        description="Source of the sleep data (e.g., device name, app)"
    )
    is_nap: bool = Field(False, description="Whether this record is for a nap")
    
    @validator('sleep_end')
    def validate_sleep_times(cls, v, values):
        if 'sleep_start' in values and v <= values['sleep_start']:
            raise ValueError("sleep_end must be after sleep_start")
        return v
    
    @validator('stages')
    def validate_stages_continuity(cls, v, values):
        if not v:
            return v
            
        # Sort stages by start time
        sorted_stages = sorted(v, key=lambda x: x.start_time)
        
        # Check for overlaps or gaps
        for i in range(1, len(sorted_stages)):
            if sorted_stages[i].start_time < sorted_stages[i-1].end_time:
                raise ValueError("Sleep stages cannot overlap")
            # Allow small gaps but log them
            gap = (sorted_stages[i].start_time - sorted_stages[i-1].end_time).total_seconds()
            if gap > 60:  # More than 1 minute gap
                # Consider if this should be an error or just a warning
                pass
        
        return sorted_stages
    
    class Config:
        schema_extra = {
            "example": {
                "sleep_start": "2023-06-07T22:00:00Z",
                "sleep_end": "2023-06-08T06:30:00Z",
                "timezone": "America/New_York",
                "stages": [
                    {"stage": "awake", "start_time": "2023-06-07T22:00:00Z", "end_time": "2023-06-07T22:15:00Z", "duration_seconds": 900},
                    {"stage": "light", "start_time": "2023-06-07T22:15:00Z", "end_time": "2023-06-07T23:00:00Z", "duration_seconds": 2700},
                    {"stage": "deep", "start_time": "2023-06-07T23:00:00Z", "end_time": "2023-06-08T00:30:00Z", "duration_seconds": 5400},
                    {"stage": "rem", "start_time": "2023-06-08T00:30:00Z", "end_time": "2023-06-08T01:00:00Z", "duration_seconds": 1800},
                    {"stage": "light", "start_time": "2023-06-08T01:00:00Z", "end_time": "2023-06-08T06:00:00Z", "duration_seconds": 18000},
                    {"stage": "awake", "start_time": "2023-06-08T06:00:00Z", "end_time": "2023-06-08T06:30:00Z", "duration_seconds": 1800}
                ],
                "total_sleep_seconds": 27900,  # 7h 45m
                "awake_seconds": 2700,  # 45m
                "light_sleep_seconds": 20700,  # 5h 45m
                "deep_sleep_seconds": 5400,  # 1h 30m
                "rem_sleep_seconds": 1800,  # 30m
                "sleep_efficiency": 86.4,  # (27900 / (27900 + 2700)) * 100
                "sleep_latency_seconds": 900,  # 15m
                "wake_after_sleep_onset_seconds": 1800,  # 30m
                "disruptions": [
                    {
                        "start_time": "2023-06-08T02:30:00Z",
                        "end_time": "2023-06-08T02:45:00Z",
                        "duration_seconds": 900,
                        "cause": "bathroom",
                        "notes": "Woke up to use the bathroom"
                    }
                ],
                "movement_count": 12,
                "quality_rating": 4,  # Good
                "rested_rating": 8,
                "room_temperature_c": 20.5,
                "noise_level_db": 35.2,
                "light_level_lux": 5.0,
                "notes": "Fell asleep quickly but woke up once during the night.",
                "source": "Oura Ring",
                "is_nap": False
            }
        }

class SleepRecordCreate(SleepRecordBase):
    """Schema for creating a new sleep record"""
    user_id: Optional[int] = Field(None, description="User ID (defaults to current user)")

class SleepRecordUpdate(BaseModel):
    """Schema for updating an existing sleep record"""
    sleep_start: Optional[datetime] = None
    sleep_end: Optional[datetime] = None
    timezone: Optional[str] = None
    quality_rating: Optional[SleepQualityRating] = None
    rested_rating: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    
    @validator('sleep_end')
    def validate_sleep_times(cls, v, values):
        if 'sleep_start' in values and v and values['sleep_start'] and v <= values['sleep_start']:
            raise ValueError("sleep_end must be after sleep_start")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "quality_rating": 4,
                "rested_rating": 7,
                "notes": "Had some trouble falling back asleep after waking up."
            }
        }

class SleepRecordResponse(SleepRecordBase, IDSchemaMixin, TimestampSchema):
    """Schema for sleep record response"""
    user_id: int = Field(..., description="User who owns this sleep record")
    
    # Derived metrics
    sleep_score: Optional[float] = Field(
        None, 
        ge=0, 
        le=100, 
        description="Overall sleep quality score (0-100)"
    )
    sleep_consistency: Optional[float] = Field(
        None, 
        ge=0, 
        le=100, 
        description="Consistency with user's typical sleep patterns (0-100)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id": 12345,
                "user_id": 456,
                "sleep_start": "2023-06-07T22:00:00Z",
                "sleep_end": "2023-06-08T06:30:00Z",
                "total_sleep_seconds": 27900,
                "sleep_efficiency": 86.4,
                "sleep_score": 82.5,
                "sleep_consistency": 78.3,
                "created_at": "2023-06-08T07:00:00Z",
                "updated_at": "2023-06-08T07:00:00Z"
            }
        }

# Sleep Analysis and Insights
class SleepStageSummary(BaseModel):
    """Summary of time spent in each sleep stage"""
    stage: SleepStageType
    duration_seconds: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "stage": "deep",
                "duration_seconds": 5400,
                "percentage": 19.4
            }
        }

class SleepAnalysis(BaseModel):
    """Detailed analysis of sleep patterns and quality"""
    # Date and duration
    date: date = Field(..., description="Date of the sleep analysis")
    total_time_in_bed_seconds: int = Field(..., ge=0, description="Total time spent in bed")
    total_sleep_seconds: int = Field(..., ge=0, description="Total time asleep")
    
    # Sleep stages
    stage_summary: List[SleepStageSummary] = Field(..., description="Breakdown by sleep stage")
    
    # Key metrics
    sleep_efficiency: float = Field(..., ge=0, le=100, description="Sleep efficiency percentage")
    sleep_latency_seconds: Optional[int] = Field(None, ge=0, description="Time to fall asleep")
    wake_after_sleep_onset_seconds: int = Field(..., ge=0, description="Time awake after sleep onset")
    rem_latency_seconds: Optional[int] = Field(None, ge=0, description="Time to first REM stage")
    
    # Disruptions
    disruption_count: int = Field(..., ge=0, description="Number of disruptions")
    disruption_duration_seconds: int = Field(..., ge=0, description="Total disruption duration")
    
    # Movement
    movement_count: Optional[int] = Field(None, ge=0, description="Number of significant movements")
    
    # Subjective ratings
    quality_rating: Optional[float] = Field(None, ge=1, le=5, description="Average quality rating")
    rested_rating: Optional[float] = Field(None, ge=1, le=10, description="Average rested rating")
    
    # Environmental factors
    avg_room_temperature_c: Optional[float] = Field(None, description="Average room temperature")
    avg_noise_level_db: Optional[float] = Field(None, ge=0, description="Average noise level")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2023-06-07",
                "total_time_in_bed_seconds": 30600,  # 8h 30m
                "total_sleep_seconds": 27900,  # 7h 45m
                "stage_summary": [
                    {"stage": "awake", "duration_seconds": 2700, "percentage": 9.7},
                    {"stage": "light", "duration_seconds": 20700, "percentage": 74.2},
                    {"stage": "deep", "duration_seconds": 5400, "percentage": 19.4},
                    {"stage": "rem", "duration_seconds": 1800, "percentage": 6.5}
                ],
                "sleep_efficiency": 86.4,
                "sleep_latency_seconds": 900,
                "wake_after_sleep_onset_seconds": 1800,
                "rem_latency_seconds": 9000,
                "disruption_count": 2,
                "disruption_duration_seconds": 1200,
                "movement_count": 15,
                "quality_rating": 4.0,
                "rested_rating": 7.5,
                "avg_room_temperature_c": 20.5,
                "avg_noise_level_db": 35.2
            }
        }

class SleepInsight(BaseModel):
    """Insights derived from sleep data analysis"""
    id: str = Field(..., description="Unique identifier for the insight")
    title: str = Field(..., description="Short title of the insight")
    description: str = Field(..., description="Detailed description")
    impact: Literal["high", "medium", "low"] = Field(..., description="Impact level")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    related_metrics: List[Dict[str, Any]] = Field(..., description="Related sleep metrics")
    recommendations: List[str] = Field(..., description="Recommended actions")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "sleep_insight_123",
                "title": "Consistent Sleep Schedule Improves Sleep Quality",
                "description": "On nights when you go to bed within 30 minutes of your usual bedtime, your sleep efficiency is 15% higher on average.",
                "impact": "high",
                "confidence": 0.92,
                "related_metrics": [
                    {"metric": "bedtime_consistency", "value": "+/- 30 min", "impact": "positive"},
                    {"metric": "sleep_efficiency", "value": "+15%", "impact": "positive"}
                ],
                "recommendations": [
                    "Try to go to bed within 30 minutes of your average bedtime (10:30 PM).",
                    "Set a consistent bedtime reminder to help establish a routine."
                ]
            }
        }

class SleepTrends(BaseModel):
    """Trends in sleep metrics over time"""
    date_range: Dict[str, date] = Field(..., description="Start and end dates of the trend period")
    metrics: Dict[str, List[Dict[str, Any]]] = Field(
        ..., 
        description="Trend data for various sleep metrics"
    )
    insights: List[SleepInsight] = Field(..., description="Insights derived from the trends")
    
    class Config:
        schema_extra = {
            "example": {
                "date_range": {"start": "2023-05-31", "end": "2023-06-06"},
                "metrics": {
                    "total_sleep_minutes": [
                        {"date": "2023-05-31", "value": 465},
                        {"date": "2023-06-01", "value": 452},
                        {"date": "2023-06-02", "value": 438},
                        {"date": "2023-06-03", "value": 510},
                        {"date": "2023-06-04", "value": 495},
                        {"date": "2023-06-05", "value": 480},
                        {"date": "2023-06-06", "value": 473}
                    ],
                    "sleep_efficiency": [
                        {"date": "2023-05-31", "value": 85.2},
                        {"date": "2023-06-01", "value": 83.7},
                        {"date": "2023-06-02", "value": 82.1},
                        {"date": "2023-06-03", "value": 89.5},
                        {"date": "2023-06-04", "value": 87.3},
                        {"date": "2023-06-05", "value": 86.8},
                        {"date": "2023-06-06", "value": 86.2}
                    ]
                },
                "insights": [
                    {
                        "id": "trend_insight_456",
                        "title": "Weekend Sleep Recovery",
                        "description": "You tend to get more sleep on weekends, with an average of 1 hour more sleep on Saturday and Sunday nights compared to weekdays.",
                        "impact": "medium",
                        "confidence": 0.88,
                        "related_metrics": [
                            {"metric": "weekend_sleep_duration", "value": "+60 min", "trend": "increasing"},
                            {"metric": "weekday_sleep_duration", "value": "-45 min", "trend": "decreasing"}
                        ],
                        "recommendations": [
                            "Consider adjusting your weekday schedule to allow for more consistent sleep duration throughout the week.",
                            "If possible, try to maintain a more consistent wake-up time, even on weekends."
                        ]
                    }
                ]
            }
        }
