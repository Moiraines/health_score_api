"""Base user schema with common fields and validations."""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from pydantic.types import constr

# Constants
USERNAME_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_]*$'  # Must start with a letter
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
DISPLAY_NAME_MIN_LENGTH = 2
DISPLAY_NAME_MAX_LENGTH = 100
BIO_MAX_LENGTH = 500

from .enums import Gender, ActivityLevel, FitnessGoal, UserRole, AccountStatus, NotificationPreference

class UserBase(BaseModel):
    """Base user schema with common fields."""
    # Authentication
    email: EmailStr = Field(..., description="User's unique email address")
    username: constr(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        regex=USERNAME_PATTERN
    ) = Field(..., description="Unique username (letters, numbers, and underscores only, starting with a letter)")
    
    # Personal Information
    first_name: Optional[constr(max_length=50)] = Field(
        None, 
        description="User's first name",
        example="John"
    )
    last_name: Optional[constr(max_length=50)] = Field(
        None, 
        description="User's last name",
        example="Doe"
    )
    date_of_birth: Optional[date] = Field(
        None, 
        description="User's date of birth (YYYY-MM-DD)",
        example="1990-01-01"
    )
    gender: Optional[Gender] = Field(
        None, 
        description="User's gender identity"
    )
    
    # Profile Information
    display_name: Optional[constr(
        min_length=DISPLAY_NAME_MIN_LENGTH,
        max_length=DISPLAY_NAME_MAX_LENGTH
    )] = Field(
        None, 
        description="User's display name (can include spaces and special characters)",
        example="John D."
    )
    bio: Optional[constr(max_length=BIO_MAX_LENGTH)] = Field(
        None, 
        description="User's biography or description",
        example="Fitness enthusiast and health coach"
    )
    profile_image_url: Optional[HttpUrl] = Field(
        None, 
        description="URL to the user's profile image"
    )
    cover_image_url: Optional[HttpUrl] = Field(
        None, 
        description="URL to the user's cover image"
    )
    
    # Settings & Preferences
    language: Optional[str] = Field(
        "en", 
        description="User's preferred language code (ISO 639-1)",
        example="en"
    )
    timezone: Optional[str] = Field(
        "UTC", 
        description="User's timezone (IANA timezone name)",
        example="America/New_York"
    )
    measurement_system: Optional[Literal["metric", "imperial"]] = Field(
        "metric", 
        description="Preferred measurement system"
    )
    
    # Fitness Information
    height_cm: Optional[float] = Field(
        None, 
        ge=50, 
        le=250, 
        description="Height in centimeters"
    )
    weight_kg: Optional[float] = Field(
        None, 
        gt=0, 
        description="Weight in kilograms"
    )
    activity_level: Optional[ActivityLevel] = Field(
        None, 
        description="User's typical activity level"
    )
    fitness_goals: Optional[List[FitnessGoal]] = Field(
        [], 
        description="User's fitness objectives"
    )
    
    # Contact Information
    phone_number: Optional[str] = Field(
        None, 
        description="User's phone number with country code",
        example="+1234567890"
    )
    
    # System Fields (not for user input)
    role: UserRole = Field(
        UserRole.USER, 
        description="User's role in the system"
    )
    status: AccountStatus = Field(
        AccountStatus.PENDING_VERIFICATION, 
        description="Account status"
    )
    
    # Timestamps (handled by database)
    created_at: Optional[datetime] = Field(
        None, 
        description="When the user account was created"
    )
    updated_at: Optional[datetime] = Field(
        None, 
        description="When the user account was last updated"
    )
    last_login_at: Optional[datetime] = Field(
        None, 
        description="When the user last logged in"
    )
    
    # Validation
    @validator('date_of_birth')
    def validate_age(cls, v):
        if v is None:
            return v
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 13:
            raise ValueError("User must be at least 13 years old")
        if age > 120:
            raise ValueError("Invalid date of birth")
        return v
    
    @validator('username')
    def username_must_be_lowercase(cls, v):
        return v.lower()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "male",
                "display_name": "John D.",
                "bio": "Fitness enthusiast and health coach",
                "language": "en",
                "timezone": "America/New_York",
                "measurement_system": "metric",
                "height_cm": 175.5,
                "weight_kg": 70.2,
                "activity_level": "moderately_active",
                "fitness_goals": ["strength", "endurance"],
                "phone_number": "+1234567890"
            }
        }
