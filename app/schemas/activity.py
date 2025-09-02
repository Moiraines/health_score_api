from datetime import datetime, time, date
from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator, HttpUrl, conint, confloat, model_validator
from pydantic.types import PositiveInt, PositiveFloat
from .base import BaseSchema
from app.domain.enums import ActivityType
from app.db.models.activity import Activity as ActivityORM

# Constants and Enums
class IntensityLevel(str, Enum):
    """Perceived intensity of the activity"""
    VERY_LIGHT = "very_light"
    LIGHT = "light"
    MODERATE = "moderate"
    VIGOROUS = "vigorous"
    MAXIMUM = "maximum"

class WeatherCondition(str, Enum):
    """Weather conditions during the activity"""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    WINDY = "windy"
    FOGGY = "foggy"
    STORMY = "stormy"
    HUMID = "humid"
    DRY = "dry"
    INDOORS = "indoors"

class ActivityStatus(str, Enum):
    """Status of the activity"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"

# Base Schemas
class Location(BaseModel):
    """Geographic location with latitude and longitude"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    accuracy: Optional[float] = Field(None, ge=0, description="Accuracy of the location in meters")
    timestamp: Optional[datetime] = Field(None, description="When this location was recorded")

class HeartRateZone(BaseModel):
    """Heart rate zone information"""
    zone: str = Field(..., description="Zone name (e.g., 'Zone 1', 'Fat Burn', 'Cardio', 'Peak')")
    min_bpm: conint(ge=30, le=250) = Field(..., description="Minimum BPM for this zone")
    max_bpm: conint(ge=30, le=250) = Field(..., description="Maximum BPM for this zone")
    time_in_zone_seconds: conint(ge=0) = Field(0, description="Time spent in this zone in seconds")

class ActivityMetrics(BaseModel):
    """Detailed metrics for an activity"""
    # Timing
    duration_seconds: conint(ge=0) = Field(0, description="Total duration in seconds")
    # active_seconds: Optional[conint(ge=0)] = Field(None, description="Active time in seconds (excluding pauses)")

    # Distance and Speed
    distance_meters: Optional[confloat(ge=0)] = Field(None, description="Total distance in meters")
    # speed_avg: Optional[confloat(ge=0)] = Field(None, description="Average speed in m/s")
    # speed_max: Optional[confloat(ge=0)] = Field(None, description="Maximum speed in m/s")
    # pace_avg: Optional[confloat(ge=0)] = Field(None, description="Average pace in seconds per kilometer")

    # Elevation
    elevation_gain: Optional[confloat(ge=0)] = Field(None, description="Total elevation gain in meters")
    elevation_loss: Optional[confloat(ge=0)] = Field(None, description="Total elevation loss in meters")
    # elevation_min: Optional[confloat(ge=-1000, le=10000)] = Field(None, description="Minimum elevation in meters")
    # elevation_max: Optional[confloat(ge=-1000, le=10000)] = Field(None, description="Maximum elevation in meters")

    # Heart Rate
    heart_rate_avg: Optional[conint(ge=30, le=250)] = Field(None, description="Average heart rate in BPM")
    heart_rate_max: Optional[conint(ge=30, le=250)] = Field(None, description="Maximum heart rate in BPM")
    # heart_rate_zones: Optional[List[HeartRateZone]] = Field(None, description="Time spent in different heart rate zones")

    # Calories and Effort
    calories_burned: Optional[conint(ge=0)] = Field(None, description="Estimated calories burned")
    # effort_score: Optional[confloat(ge=0, le=10)] = Field(None, description="Perceived effort on a scale of 1-10")
    # intensity: Optional[IntensityLevel] = Field(None, description="Perceived intensity level")

    # Repetition-based activities
    # repetitions: Optional[conint(ge=0)] = Field(None, description="Number of repetitions (for strength training)")
    # sets: Optional[conint(ge=0)] = Field(None, description="Number of sets (for strength training)")
    # weight_kg: Optional[confloat(ge=0, le=1000)] = Field(None, description="Weight used in kg")

    # GPS and Route
    # start_location: Optional[Location] = Field(None, description="Starting location")
    # end_location: Optional[Location] = Field(None, description="Ending location")
    # route: Optional[List[Location]] = Field(None, description="Detailed route points")

    # Additional Metrics
    # steps: Optional[conint(ge=0)] = Field(None, description="Step count for walking/running")
    # strokes: Optional[conint(ge=0)] = Field(None, description="Stroke count for swimming/rowing")
    # pool_length: Optional[confloat(ge=0)] = Field(None, description="Pool length in meters (for swimming)")
    # pool_laps: Optional[conint(ge=0)] = Field(None, description="Number of pool laps (for swimming)")
    # cadence_avg: Optional[conint(ge=0, le=300)] = Field(None, description="Average cadence in SPM (steps per minute)")
    # cadence_max: Optional[conint(ge=0, le=300)] = Field(None, description="Maximum cadence in SPM")

# Main Activity Schemas
class ActivityBase(BaseSchema):
    """Base schema for activity data"""
    activity_type: ActivityType = Field(..., description="Type of physical activity")
    name: Optional[str] = Field(None, max_length=100, description="Custom name for the activity")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description or notes")

    # Timing
    start_time: datetime = Field(..., description="When the activity started")
    end_time: Optional[datetime] = Field(None, description="When the activity ended")
    # timezone: str = Field("UTC", description="Timezone where the activity was recorded")

    # Status and Visibility
    # status: ActivityStatus = Field(ActivityStatus.COMPLETED, description="Current status of the activity")
    # is_race: bool = Field(False, description="Whether this was a race/competition")
    # is_manual: bool = Field(False, description="Whether this was manually entered")
    # is_private: bool = Field(False, description="Whether this activity is private")

    # Equipment and Environment
    # equipment: Optional[List[str]] = Field(None, description="List of equipment used")
    # weather: Optional[WeatherCondition] = Field(None, description="Weather conditions")
    # temperature_c: Optional[confloat(ge=-50, le=60)] = Field(None, description="Temperature in Celsius")
    # humidity: Optional[confloat(ge=0, le=100)] = Field(None, description="Humidity percentage")

    # Metrics (embedded document)
    metrics: ActivityMetrics = Field(default_factory=ActivityMetrics, description="Detailed activity metrics")

    # Media and External References
    # photo_urls: Optional[List[HttpUrl]] = Field(None, description="URLs to activity photos")
    # external_id: Optional[str] = Field(None, description="ID from external service (e.g., Strava, Garmin, Apple Health)")
    # external_source: Optional[str] = Field(None, description="Source of the external ID")

    class Config:
        json_schema_extra = {
            "example": {
                "activity_type": "running",
                "name": "Morning Run",
                "description": "Easy recovery run around the park",
                "start_time": "2025-06-02T07:30:00Z",
                "end_time": "2025-09-02T08:15:00Z",
                # "timezone": "America/New_York",
                # "status": "completed",
                # "is_race": False,
                # "is_manual": False,
                # "is_private": False,
                # "equipment": ["Nike Pegasus 38", "Garmin Forerunner 245"],
                # "weather": "clear",
                # "temperature_c": 18.5,
                # "humidity": 65.0,
                "metrics": {
                    "duration_seconds": 2700,
                    "distance_meters": 6000,
                    # "speed_avg": 3.3,
                    # "speed_max": 4.5,
                    "heart_rate_avg": 145,
                    "heart_rate_max": 162,
                    "calories_burned": 420,
                    # "steps": 7500,
                    # "cadence_avg": 170,
                    "elevation_gain": 120.5,
                    "elevation_loss": 118.2
                },
                # "photo_urls": ["https://example.com/photos/run1.jpg"],
                # "external_id": "strava_1234567890",
                # "external_source": "strava"
            }
        }

class ActivityCreate(ActivityBase):
    """Schema for creating a new activity"""
    user_id: Optional[int] = Field(None, description="User ID (defaults to current user)")

    @validator('end_time')
    def validate_times(cls, v, values):
        if 'start_time' in values and v:
            if v < values['start_time']:
                raise ValueError("End time must be after start time")
        return v

class ActivityUpdate(BaseModel):
    """Schema for updating an existing activity"""
    name: Optional[str] = Field(None, max_length=100, description="Custom name for the activity")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description or notes")
    # status: Optional[ActivityStatus] = None
    # is_private: Optional[bool] = None
    metrics: Optional[ActivityMetrics] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Morning Run",
                "description": "Added more details about the route",
                # "is_private": True,
                "metrics": {
                    "duration_seconds": 2700,
                    "distance_meters": 6000,
                    # "speed_avg": 3.3,
                    # "speed_max": 4.5,
                    "heart_rate_avg": 145,
                    "heart_rate_max": 162,
                    "calories_burned": 420,
                    # "steps": 7500,
                    # "cadence_avg": 170,
                    "elevation_gain": 120.5,
                    "elevation_loss": 118.2
                },
            }
        }

class ActivityResponse(ActivityBase):
    """Schema for activity response (includes read-only fields)"""
    id: int = Field(..., description="Unique identifier for the activity")
    user_id: int = Field(..., description="User who performed the activity")
    created_at: datetime = Field(..., description="When the activity was created in the system")
    updated_at: Optional[datetime] = Field(
        None, description="When the activity was last updated"
    )

    @model_validator(mode="before") # type: ignore[call-overload]
    @classmethod
    def _from_orm(cls, data: Any):
        if isinstance(data, ActivityORM):
            obj = data
            return {
                "id": obj.id,
                "user_id": obj.user_id,
                "activity_type": obj.activity_type,  # enum -> str автоматично
                "name": obj.custom_activity_name,
                "description": obj.notes,
                "start_time": obj.start_time,
                "end_time": obj.end_time,
                "metrics": {
                    "duration_seconds": (obj.duration_minutes * 60) if obj.duration_minutes is not None else None,
                    "distance_meters": obj.distance_meters,
                    "elevation_gain": obj.elevation_gain_meters,
                    "elevation_loss": obj.elevation_loss_meters,
                    "heart_rate_avg": obj.average_heart_rate,
                    "heart_rate_max": obj.max_heart_rate,
                    "calories_burned": obj.calories_burned,
                },
                "created_at": obj.created_at,
                "updated_at": obj.updated_at,
            }
        # ако вече е dict – оставяме както е
        return data

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 12345,
                "user_id": 987,
                "created_at": "2025-09-02T08:20:00Z",
                "updated_at": "2025-09-02T10:15:00Z",
                "activity_type": "running",
                "name": "Morning Run",
                "description": "Easy recovery run around the park",
                "start_time": "2025-09-02T07:30:00Z",
                "end_time": "2025-09-02T08:15:00Z",
                "metrics": {
                    "duration_seconds": 2700,
                    "distance_meters": 6000,
                    "elevation_gain": 120.5,
                    "elevation_loss": 118.2,
                    "heart_rate_avg": 145,
                    "heart_rate_max": 162,
                    "calories_burned": 420
                }
            }
        }

class Activity(ActivityResponse):
    """Compat alias so endpoints can import Activity directly."""
    pass

class ActivityListResponse(BaseModel):
    """Schema for paginated list of activities"""
    items: List[ActivityResponse] = Field(..., description="List of activities")
    total: int = Field(..., description="Total number of activities")
    page: int = Field(..., description="Current page number")
    pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 12345,
                        "activity_type": "running",
                        "name": "Morning Run",
                        "start_time": "2023-06-07T07:30:00Z",
                        "duration_seconds": 2700,
                        "distance_meters": 6000,
                        "calories_burned": 420
                    },
                    {
                        "id": 12344,
                        "activity_type": "weight_training",
                        "name": "Chest & Back",
                        "start_time": "2023-06-06T18:00:00Z",
                        "duration_seconds": 3600,
                        "calories_burned": 320
                    }
                ],
                "total": 2,
                "page": 1,
                "pages": 1
            }
        }

# Workout Plan Schemas
class ExerciseSet(BaseModel):
    """Schema for a single set of an exercise"""
    set_number: conint(ge=1) = Field(..., description="Set number in the sequence")
    target_reps: Optional[conint(ge=1)] = Field(None, description="Target number of repetitions")
    completed_reps: Optional[conint(ge=0)] = Field(None, description="Actual number of repetitions completed")
    target_weight_kg: Optional[confloat(ge=0)] = Field(None, description="Target weight in kilograms")
    completed_weight_kg: Optional[confloat(ge=0)] = Field(None, description="Actual weight used in kilograms")
    rpe: Optional[confloat(ge=1, le=10)] = Field(None, description="Rate of Perceived Exertion (1-10)")
    rest_seconds: Optional[conint(ge=0)] = Field(None, description="Rest time after this set in seconds")
    notes: Optional[str] = Field(None, description="Additional notes for this set")

class WorkoutExercise(BaseModel):
    """Schema for an exercise within a workout"""
    exercise_id: int = Field(..., description="Reference to the exercise")
    exercise_name: str = Field(..., description="Name of the exercise")
    notes: Optional[str] = Field(None, description="Exercise-specific notes")
    superset_with: Optional[str] = Field(None, description="ID of exercise to superset with")
    sets: List[ExerciseSet] = Field(..., min_items=1, description="List of sets for this exercise")

    @validator('sets')
    def validate_sets_order(cls, v):
        set_numbers = [s.set_number for s in v]
        if sorted(set_numbers) != list(range(1, len(v) + 1)):
            raise ValueError("Set numbers must be sequential starting from 1")
        return v

class WorkoutPlanBase(BaseModel):
    """Base schema for workout plans"""
    name: str = Field(..., max_length=100, description="Name of the workout plan")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description")
    is_template: bool = Field(False, description="Whether this is a reusable template")
    difficulty: Optional[Literal["beginner", "intermediate", "advanced"]] = Field(None, description="Difficulty level")
    estimated_duration_minutes: Optional[conint(ge=1)] = Field(None, description="Estimated duration in minutes")
    target_muscles: List[str] = Field(default_factory=list, description="Target muscle groups")
    equipment_required: List[str] = Field(default_factory=list, description="Required equipment")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Upper Body Strength",
                "description": "Focused on building upper body strength with compound movements",
                "is_template": True,
                "difficulty": "intermediate",
                "estimated_duration_minutes": 60,
                "target_muscles": ["chest", "back", "shoulders", "arms"],
                "equipment_required": ["barbell", "dumbbells", "bench", "pull-up bar"]
            }
        }

class WorkoutPlanCreate(WorkoutPlanBase):
    """Schema for creating a new workout plan"""
    exercises: List[WorkoutExercise] = Field(..., min_items=1, description="Exercises in the workout")

class WorkoutPlanResponse(WorkoutPlanBase):
    """Schema for workout plan response"""
    id: int
    user_id: Optional[int] = Field(None, description="Owner of the plan (null for system templates)")
    created_at: datetime
    updated_at: datetime
    exercises: List[WorkoutExercise]

    class Config:
        from_attributes = True
