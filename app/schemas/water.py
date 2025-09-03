from datetime import datetime, time
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, conint, confloat

from .base import BaseSchema, TimestampSchema, IDSchemaMixin

# Enums for water intake tracking
class WaterSource(str, Enum):
    """Sources of water intake"""
    TAP_WATER = "tap_water"
    BOTTLED_WATER = "bottled_water"
    FILTERED_WATER = "filtered_water"
    SPARKLING_WATER = "sparkling_water"
    TEA = "tea"
    COFFEE = "coffee"
    JUICE = "juice"
    MILK = "milk"
    SPORTS_DRINK = "sports_drink"
    ALCOHOL = "alcohol"
    OTHER_BEVERAGE = "other_beverage"
    FOOD = "food"
    OTHER = "other"

class WaterIntakeUnit(str, Enum):
    """Units for measuring water intake"""
    MILLILITERS = "ml"
    LITERS = "L"
    OUNCES = "oz"
    CUPS = "cups"
    BOTTLES = "bottles"

class HydrationLevel(str, Enum):
    """Levels of hydration status"""
    SEVERELY_DEHYDRATED = "severely_dehydrated"
    DEHYDRATED = "dehydrated"
    MILDY_DEHYDRATED = "mildy_dehydrated"
    WELL_HYDRATED = "well_hydrated"
    OVER_HYDRATED = "over_hydrated"

# Base Schemas
class WaterIntakeBase(BaseSchema):
    """Base schema for water intake entries"""
    amount: float = Field(..., gt=0, description="Amount of water consumed")
    unit: WaterIntakeUnit = Field(..., description="Unit of measurement")
    
    # Timing
    consumed_at: datetime = Field(..., description="When the water was consumed")
    timezone: str = Field("UTC", description="Timezone where the intake was recorded")
    
    # Source and details
    source: WaterSource = Field(..., description="Source of the water/beverage")
    source_details: Optional[str] = Field(
        None, 
        description="Additional details about the source (e.g., brand, type)",
        max_length=100
    )
    
    # Hydration factors
    hydration_factor: float = Field(
        1.0, 
        ge=0, 
        le=1.5, 
        description="Hydration effectiveness factor (1.0 = water, <1.0 = dehydrating, >1.0 = hydrating)"
    )
    
    # Additional metadata
    notes: Optional[str] = Field(
        None, 
        description="Additional notes about the intake",
        max_length=500
    )
    
    # Temperature in Celsius (optional)
    temperature_c: Optional[float] = Field(
        None, 
        description="Temperature of the beverage in Celsius",
        ge=0,
        le=100
    )
    
    # Was this logged manually or automatically?
    is_manual_entry: bool = Field(
        True, 
        description="Whether the entry was logged manually or automatically"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "amount": 500,
                "unit": "ml",
                "consumed_at": "2023-06-08T10:30:00Z",
                "timezone": "America/New_York",
                "source": "filtered_water",
                "source_details": "Berkey filter",
                "hydration_factor": 1.0,
                "notes": "Drank during morning workout",
                "temperature_c": 22.0,
                "is_manual_entry": True
            }
        }
    
    @validator('consumed_at')
    def validate_consumed_at_not_future(cls, v):
        if v > datetime.utcnow():
            raise ValueError("consumed_at cannot be in the future")
        return v

class WaterIntakeCreate(WaterIntakeBase):
    """Schema for creating a new water intake entry"""
    user_id: Optional[int] = Field(None, description="User ID (defaults to current user)")

class WaterIntakeUpdate(BaseModel):
    """Schema for updating an existing water intake entry"""
    amount: Optional[float] = Field(None, gt=0)
    unit: Optional[WaterIntakeUnit] = None
    consumed_at: Optional[datetime] = None
    source: Optional[WaterSource] = None
    source_details: Optional[str] = Field(None, max_length=100)
    hydration_factor: Optional[float] = Field(None, ge=0, le=1.5)
    notes: Optional[str] = Field(None, max_length=500)
    temperature_c: Optional[float] = Field(None, ge=0, le=100)
    
    @validator('consumed_at')
    def validate_consumed_at_not_future(cls, v):
        if v and v > datetime.utcnow():
            raise ValueError("consumed_at cannot be in the future")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "amount": 600,
                "notes": "Updated amount after measuring more precisely"
            }
        }

class WaterIntakeResponse(WaterIntakeBase, IDSchemaMixin, TimestampSchema):
    """Schema for water intake response"""
    user_id: int = Field(..., description="User who owns this intake record")
    
    # Converted amounts for consistency
    amount_ml: float = Field(..., description="Amount in milliliters")
    amount_oz: float = Field(..., description="Amount in fluid ounces")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 12345,
                "user_id": 456,
                "amount": 500,
                "unit": "ml",
                "amount_ml": 500.0,
                "amount_oz": 16.9,
                "consumed_at": "2023-06-08T10:30:00Z",
                "created_at": "2023-06-08T10:31:22Z",
                "updated_at": "2023-06-08T10:31:22Z"
            }
        }

# Daily Summary and Analysis
class DailyWaterSummary(BaseModel):
    """Daily summary of water intake"""
    date: date = Field(..., description="Date of the summary")
    
    # Total intake
    total_ml: float = Field(..., ge=0, description="Total water intake in milliliters")
    total_oz: float = Field(..., ge=0, description="Total water intake in fluid ounces")
    
    # Intake by source
    intake_by_source: Dict[WaterSource, float] = Field(
        default_factory=dict, 
        description="Water intake grouped by source in milliliters"
    )
    
    # Intake by time of day
    intake_by_hour: Dict[int, float] = Field(
        default_factory=dict, 
        description="Water intake by hour of day (0-23) in milliliters"
    )
    
    # Comparison to goal
    goal_ml: Optional[float] = Field(None, ge=0, description="Daily water intake goal in milliliters")
    goal_achieved: bool = Field(..., description="Whether the daily goal was achieved")
    goal_percentage: float = Field(
        ..., 
        ge=0, 
        description="Percentage of daily goal achieved (can exceed 100%)"
    )
    
    # Hydration status
    hydration_level: HydrationLevel = Field(..., description="Overall hydration status for the day")
    
    # Number of intake entries
    entry_count: int = Field(..., ge=0, description="Number of water intake entries")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2023-06-08",
                "total_ml": 2750.0,
                "total_oz": 93.0,
                "intake_by_source": {
                    "filtered_water": 2000.0,
                    "tea": 350.0,
                    "coffee": 400.0
                },
                "intake_by_hour": {
                    8: 300.0,
                    10: 500.0,
                    12: 400.0,
                    14: 350.0,
                    16: 400.0,
                    18: 400.0,
                    20: 400.0
                },
                "goal_ml": 3000.0,
                "goal_achieved": False,
                "goal_percentage": 91.7,
                "hydration_level": "well_hydrated",
                "entry_count": 7
            }
        }

class HydrationAnalysis(BaseModel):
    """Analysis of hydration patterns and recommendations"""
    date_range: Dict[str, date] = Field(..., description="Start and end dates of the analysis period")
    
    # Summary metrics
    average_daily_intake_ml: float = Field(..., ge=0, description="Average daily intake in milliliters")
    average_daily_intake_oz: float = Field(..., ge=0, description="Average daily intake in fluid ounces")
    
    # Comparison to goals
    daily_goal_ml: Optional[float] = Field(None, ge=0, description="Daily water intake goal in milliliters")
    goal_achievement_rate: float = Field(
        ..., 
        ge=0, 
        description="Percentage of days the goal was met"
    )
    
    # Patterns
    intake_by_weekday: Dict[str, float] = Field(
        ..., 
        description="Average intake by day of week (0=Monday, 6=Sunday) in milliliters"
    )
    intake_by_hour: Dict[int, float] = Field(
        ..., 
        description="Average intake by hour of day (0-23) in milliliters"
    )
    
    # Sources
    source_distribution: Dict[WaterSource, float] = Field(
        ..., 
        description="Percentage distribution of water sources"
    )
    
    # Hydration status
    hydration_level_distribution: Dict[HydrationLevel, float] = Field(
        ..., 
        description="Distribution of hydration status across the period"
    )
    
    # Insights
    insights: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Key insights about hydration patterns"
    )
    
    # Recommendations
    recommendations: List[str] = Field(
        default_factory=list, 
        description="Personalized recommendations for improving hydration"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "date_range": {"start": "2023-05-31", "end": "2023-06-06"},
                "average_daily_intake_ml": 2650.0,
                "average_daily_intake_oz": 89.6,
                "daily_goal_ml": 3000.0,
                "goal_achievement_rate": 42.9,
                "intake_by_weekday": {
                    "Monday": 2800.0,
                    "Tuesday": 2700.0,
                    "Wednesday": 2600.0,
                    "Thursday": 2500.0,
                    "Friday": 2900.0,
                    "Saturday": 2400.0,
                    "Sunday": 2300.0
                },
                "intake_by_hour": {
                    8: 300.0,
                    10: 400.0,
                    12: 350.0,
                    14: 300.0,
                    16: 400.0,
                    18: 300.0,
                    20: 200.0
                },
                "source_distribution": {
                    "filtered_water": 65.0,
                    "tea": 15.0,
                    "coffee": 15.0,
                    "other_beverage": 5.0
                },
                "hydration_level_distribution": {
                    "well_hydrated": 57.1,
                    "mildy_dehydrated": 28.6,
                    "dehydrated": 14.3,
                    "severely_dehydrated": 0.0,
                    "over_hydrated": 0.0
                },
                "insights": [
                    {
                        "title": "Weekend Hydration Drop",
                        "description": "Your water intake drops by an average of 18% on weekends compared to weekdays.",
                        "impact": "medium"
                    },
                    {
                        "title": "Afternoon Slump",
                        "description": "Your water intake decreases significantly in the afternoon (2-5 PM).",
                        "impact": "low"
                    }
                ],
                "recommendations": [
                    "Set reminders to drink water in the afternoon when your intake tends to drop.",
                    "Keep a water bottle with you on weekends to maintain consistent hydration.",
                    "Aim to drink at least 500ml of water with each meal to help reach your daily goal."
                ]
            }
        }

class HydrationGoal(BaseModel):
    """User's hydration goal settings"""
    daily_target_ml: float = Field(
        3000.0, 
        ge=500, 
        le=10000, 
        description="Daily water intake target in milliliters"
    )
    
    # Custom schedule for reminders
    reminder_enabled: bool = Field(
        True, 
        description="Whether hydration reminders are enabled"
    )
    reminder_start_time: time = Field(
        time(8, 0), 
        description="Time to start sending reminders"
    )
    reminder_end_time: time = Field(
        time(20, 0), 
        description="Time to stop sending reminders"
    )
    reminder_frequency_minutes: int = Field(
        120, 
        ge=15, 
        le=240, 
        description="Minutes between reminders"
    )
    
    # Weekday-specific settings
    reminder_days: List[int] = Field(
        [0, 1, 2, 3, 4, 5, 6], 
        description="Days to send reminders (0=Monday, 6=Sunday)",
        min_items=1,
        max_items=7
    )
    
    # Notification preferences
    notification_enabled: bool = Field(
        True, 
        description="Whether to send push notifications"
    )
    email_notifications: bool = Field(
        False, 
        description="Whether to send email notifications"
    )
    
    # Adjustments
    adjust_for_activity: bool = Field(
        True, 
        description="Automatically adjust goals based on activity level"
    )
    adjust_for_weather: bool = Field(
        True, 
        description="Automatically adjust goals based on weather (temperature/humidity)"
    )
    
    @validator('reminder_end_time')
    def validate_reminder_times(cls, v, values):
        if 'reminder_start_time' in values and v <= values['reminder_start_time']:
            raise ValueError("reminder_end_time must be after reminder_start_time")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "daily_target_ml": 3000.0,
                "reminder_enabled": True,
                "reminder_start_time": "08:00:00",
                "reminder_end_time": "20:00:00",
                "reminder_frequency_minutes": 120,
                "reminder_days": [0, 1, 2, 3, 4, 5, 6],
                "notification_enabled": True,
                "email_notifications": False,
                "adjust_for_activity": True,
                "adjust_for_weather": True
            }
        }
