from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from pydantic.types import constr, conint, confloat
from .auth import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_REGEX

# Constants
USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
DISPLAY_NAME_MIN_LENGTH = 2
DISPLAY_NAME_MAX_LENGTH = 100
BIO_MAX_LENGTH = 500

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"  # Little or no exercise
    LIGHTLY_ACTIVE = "lightly_active"  # Light exercise/sports 1-3 days/week
    MODERATELY_ACTIVE = "moderately_active"  # Moderate exercise/sports 3-5 days/week
    VERY_ACTIVE = "very_active"  # Hard exercise/sports 6-7 days a week
    EXTRA_ACTIVE = "extra_active"  # Very hard exercise & physical job or 2x training

class FitnessGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    GENERAL_FITNESS = "general_fitness"
    SPORT_SPECIFIC = "sport_specific"
    REHABILITATION = "rehabilitation"

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr = Field(..., description="User's email address")
    username: constr(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        pattern=USERNAME_PATTERN
    ) = Field(..., description="Unique username (letters, numbers, and underscores only)")

    # Personal Information
    first_name: Optional[constr(max_length=50)] = Field(
        None, description="User's first name"
    )
    last_name: Optional[constr(max_length=50)] = Field(
        None, description="User's last name"
    )

    # Profile Information
    display_name: Optional[constr(max_length=DISPLAY_NAME_MAX_LENGTH)] = Field(
        None, description="User's display name (can include spaces and special characters)"
    )
    bio: Optional[constr(max_length=BIO_MAX_LENGTH)] = Field(
        None, description="User's biography or description"
    )
    date_of_birth: Optional[date] = Field(
        None, description="User's date of birth (YYYY-MM-DD)"
    )
    gender: Optional[Gender] = Field(
        None, description="User's gender identity"
    )

    # Fitness Profile
    height_cm: Optional[confloat(gt=0, le=300)] = Field(
        None, description="User's height in centimeters"
    )
    weight_kg: Optional[confloat(gt=0, le=1000)] = Field(
        None, description="User's weight in kilograms"
    )
    activity_level: Optional[ActivityLevel] = Field(
        None, description="User's typical activity level"
    )
    fitness_goals: Optional[List[FitnessGoal]] = Field(
        default_factory=list, description="User's fitness goals"
    )

    # Contact Information
    phone_number: Optional[constr(max_length=20)] = Field(
        None, description="User's phone number (international format)"
    )
    profile_picture_url: Optional[HttpUrl] = Field(
        None, description="URL to user's profile picture"
    )

    # Settings
    language: Optional[constr(min_length=2, max_length=10)] = Field(
        "en", description="User's preferred language code (e.g., 'en', 'es', 'fr')"
    )
    timezone: Optional[str] = Field(
        "UTC", description="User's timezone (e.g., 'America/New_York')"
    )
    units: Optional[Literal["metric", "imperial"]] = Field(
        "metric", description="Preferred measurement system"
    )

    # Email preferences
    email_notifications: bool = Field(
        True, description="Whether to receive email notifications"
    )
    marketing_emails: bool = Field(
        False, description="Whether to receive marketing emails"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "fitness_enthusiast",
                "first_name": "Alex",
                "last_name": "Johnson",
                "display_name": "Alex J.",
                "bio": "Fitness enthusiast and health coach",
                "date_of_birth": "1990-01-15",
                "gender": "non_binary",
                "height_cm": 175.5,
                "weight_kg": 70.2,
                "activity_level": "moderately_active",
                "fitness_goals": ["strength", "endurance"],
                "phone_number": "+1234567890",
                "profile_picture_url": "https://example.com/profiles/alex.jpg",
                "language": "en",
                "timezone": "America/New_York",
                "units": "metric",
                "email_notifications": True,
                "marketing_emails": False
            }
        }

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        pattern=PASSWORD_REGEX,
        description=f"Password must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character"
    )

    @validator('date_of_birth')
    def validate_age(cls, v):
        if v:
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 13:
                raise ValueError("Users must be at least 13 years old")
            if age > 120:
                raise ValueError("Invalid date of birth")
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    username: Optional[constr(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        pattern=USERNAME_PATTERN
    )] = None

    # Personal Information
    first_name: Optional[constr(max_length=50)] = None
    last_name: Optional[constr(max_length=50)] = None
    display_name: Optional[constr(max_length=DISPLAY_NAME_MAX_LENGTH)] = None
    bio: Optional[constr(max_length=BIO_MAX_LENGTH)] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None

    # Fitness Profile
    height_cm: Optional[confloat(gt=0, le=300)] = None
    weight_kg: Optional[confloat(gt=0, le=1000)] = None
    activity_level: Optional[ActivityLevel] = None
    fitness_goals: Optional[List[FitnessGoal]] = None

    # Contact Information
    phone_number: Optional[constr(max_length=20)] = None
    profile_picture_url: Optional[HttpUrl] = None

    # Settings
    language: Optional[constr(min_length=2, max_length=10)] = None
    timezone: Optional[str] = None
    units: Optional[Literal["metric", "imperial"]] = None

    # Email preferences
    email_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "updated.email@example.com",
                "display_name": "Alex J. (Updated)",
                "bio": "Health and fitness coach | Marathon runner | Nutrition enthusiast",
                "weight_kg": 68.5,
                "fitness_goals": ["endurance", "weight_loss"],
                "timezone": "America/Los_Angeles"
            }
        }

class UserPublic(UserBase):
    """Public user profile (visible to other users)"""
    id: int
    created_at: datetime
    last_active: Optional[datetime] = None
    is_public: bool = Field(True, description="Whether the profile is publicly visible")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "username": "fitness_enthusiast",
                "display_name": "Alex J.",
                "bio": "Fitness enthusiast and health coach",
                "created_at": "2023-01-01T12:00:00Z",
                "last_active": "2023-06-07T15:30:00Z",
                "is_public": True
            }
        }

class UserPrivate(UserPublic):
    """Extended user profile with private information (visible only to the user)"""
    email_verified: bool = Field(False, description="Whether the email has been verified")
    phone_verified: bool = Field(False, description="Whether the phone number has been verified")
    is_active: bool = Field(True, description="Whether the account is active")
    is_superuser: bool = Field(False, description="Whether the user has superuser privileges")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "username": "fitness_enthusiast",
                "display_name": "Alex J.",
                "email_verified": True,
                "phone_verified": False,
                "is_active": True,
                "is_superuser": False,
                "created_at": "2023-01-01T12:00:00Z",
                "last_active": "2023-06-07T15:30:00Z",
                "is_public": True
            }
        }

class UserInDB(UserPrivate):
    """Complete user model as stored in the database"""
    hashed_password: str = Field(..., description="Hashed password (never returned in API responses)")

    class Config:
        from_attributes = True

class UserStats(BaseModel):
    """User statistics and achievements"""
    total_workouts: int = Field(0, description="Total number of workouts completed")
    total_steps: int = Field(0, description="Total steps recorded")
    total_distance_km: float = Field(0.0, description="Total distance covered in kilometers")
    total_calories_burned: int = Field(0, description="Total calories burned")
    current_streak_days: int = Field(0, description="Current streak in days")
    longest_streak_days: int = Field(0, description="Longest streak in days")
    achievement_count: int = Field(0, description="Number of achievements unlocked")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_workouts": 42,
                "total_steps": 125000,
                "total_distance_km": 875.5,
                "total_calories_burned": 42500,
                "current_streak_days": 7,
                "longest_streak_days": 30,
                "achievement_count": 15
            }
        }

class UserProfileResponse(BaseModel):
    """Complete user profile response"""
    user: UserPrivate
    stats: UserStats

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 123,
                    "email": "user@example.com",
                    "username": "fitness_enthusiast",
                    "display_name": "Alex J.",
                    "email_verified": True,
                    "phone_verified": False,
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2023-01-01T12:00:00Z",
                    "last_active": "2023-06-07T15:30:00Z",
                    "is_public": True
                },
                "stats": {
                    "total_workouts": 42,
                    "total_steps": 125000,
                    "total_distance_km": 875.5,
                    "total_calories_burned": 42500,
                    "current_streak_days": 7,
                    "longest_streak_days": 30,
                    "achievement_count": 15
                }
            }
        }
