"""Response schemas for user-related endpoints."""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, constr, EmailStr

from .enums import Gender, ActivityLevel, FitnessGoal, UserRole, AccountStatus
from ..base import IDSchemaMixin, TimestampSchema

class UserPublicResponse(IDSchemaMixin):
    """Public user profile data (visible to anyone)."""
    username: str = Field(..., description="User's username")
    display_name: Optional[str] = Field(
        None, 
        description="User's display name"
    )
    profile_image_url: Optional[HttpUrl] = Field(
        None, 
        description="URL to the user's profile image"
    )
    cover_image_url: Optional[HttpUrl] = Field(
        None, 
        description="URL to the user's cover image"
    )
    bio: Optional[str] = Field(
        None, 
        description="User's biography or description"
    )
    created_at: datetime = Field(
        ..., 
        description="When the user joined the platform"
    )

    # Stats (counts)
    follower_count: int = Field(
        0, 
        description="Number of followers"
    )
    following_count: int = Field(
        0, 
        description="Number of users this user is following"
    )
    activity_count: int = Field(
        0, 
        description="Number of activities shared"
    )

    # Fitness information (if public)
    fitness_goals: Optional[List[FitnessGoal]] = Field(
        None, 
        description="User's fitness objectives (if public)"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 123,
                "username": "johndoe",
                "display_name": "John D.",
                "profile_image_url": "https://example.com/profiles/johndoe.jpg",
                "cover_image_url": "https://example.com/covers/johndoe.jpg",
                "bio": "Fitness enthusiast and health coach",
                "created_at": "2023-01-15T10:30:00Z",
                "follower_count": 42,
                "following_count": 15,
                "activity_count": 28,
                "fitness_goals": ["strength", "endurance"]
            }
        }
    }

class UserPrivateResponse(UserPublicResponse, TimestampSchema):
    """Private user data (visible only to the user and admins)."""
    email: EmailStr = Field(..., description="User's email address")
    first_name: Optional[str] = Field(
        None, 
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        None, 
        description="User's last name"
    )
    date_of_birth: Optional[date] = Field(
        None, 
        description="User's date of birth (YYYY-MM-DD)"
    )
    gender: Optional[Gender] = Field(
        None, 
        description="User's gender identity"
    )

    # Contact information
    phone_number: Optional[str] = Field(
        None, 
        description="User's phone number with country code"
    )

    # Settings & Preferences
    language: str = Field(
        "en", 
        description="User's preferred language code (ISO 639-1)"
    )
    timezone: str = Field(
        "UTC", 
        description="User's timezone (IANA timezone name)"
    )
    measurement_system: str = Field(
        "metric", 
        description="Preferred measurement system"
    )

    # Fitness Information
    height_cm: Optional[float] = Field(
        None, 
        description="Height in centimeters"
    )
    weight_kg: Optional[float] = Field(
        None, 
        description="Weight in kilograms"
    )
    activity_level: Optional[ActivityLevel] = Field(
        None, 
        description="User's typical activity level"
    )

    # System fields
    role: UserRole = Field(
        UserRole.USER, 
        description="User's role in the system"
    )
    status: AccountStatus = Field(
        AccountStatus.ACTIVE, 
        description="Account status"
    )
    email_verified: bool = Field(
        False, 
        description="Whether the email address has been verified"
    )
    phone_verified: bool = Field(
        False, 
        description="Whether the phone number has been verified"
    )

    # Timestamps
    last_login_at: Optional[datetime] = Field(
        None, 
        description="When the user last logged in"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            **UserPublicResponse.model_config["json_schema_extra"]["example"],
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "phone_number": "+1234567890",
            "language": "en",
            "timezone": "America/New_York",
            "measurement_system": "metric",
            "height_cm": 175.5,
            "weight_kg": 70.2,
            "activity_level": "moderately_active",
            "role": "user",
            "status": "active",
            "email_verified": True,
            "phone_verified": False,
            "created_at": "2023-01-15T10:30:00Z",
            "updated_at": "2023-06-08T14:30:00Z",
            "last_login_at": "2023-06-08T14:25:00Z"
        }
    }

class UserStatsResponse(BaseModel):
    """User statistics and achievements."""
    user_id: int = Field(..., description="User ID")

    # Activity stats
    total_activities: int = Field(
        0, 
        description="Total number of activities logged"
    )
    total_distance_km: float = Field(
        0.0, 
        description="Total distance covered in kilometers"
    )
    total_duration_minutes: int = Field(
        0, 
        description="Total duration of all activities in minutes"
    )
    total_calories_burned: int = Field(
        0, 
        description="Total calories burned across all activities"
    )

    # Streaks
    current_streak_days: int = Field(
        0, 
        description="Current streak in days"
    )
    longest_streak_days: int = Field(
        0, 
        description="Longest streak in days"
    )

    # Achievements
    achievement_count: int = Field(
        0, 
        description="Number of achievements unlocked"
    )

    # Recent activity
    recent_activities: List[Dict[str, Any]] = Field(
        [], 
        description="List of recent activities"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "user_id": 123,
                "total_activities": 42,
                "total_distance_km": 256.8,
                "total_duration_minutes": 7560,
                "total_calories_burned": 42500,
                "current_streak_days": 7,
                "longest_streak_days": 30,
                "achievement_count": 8,
                "recent_activities": [
                    {"date": "2023-06-08", "type": "running", "distance_km": 5.2, "duration_minutes": 28},
                    {"date": "2023-06-07", "type": "strength_training", "duration_minutes": 45},
                    {"date": "2023-06-05", "type": "cycling", "distance_km": 15.7, "duration_minutes": 42}
                ]
            }
        }
    }

class UserSearchResult(BaseModel):
    """User search result item."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    display_name: Optional[str] = Field(
        None, 
        description="User's display name"
    )
    profile_image_url: Optional[HttpUrl] = Field(
        None, 
        description="URL to the user's profile image"
    )
    is_following: bool = Field(
        False, 
        description="Whether the current user is following this user"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 123,
                "username": "johndoe",
                "display_name": "John D.",
                "profile_image_url": "https://example.com/profiles/johndoe.jpg",
                "is_following": True
            }
        }
    }

class UserListResponse(BaseModel):
    """Paginated list of users."""
    items: List[UserSearchResult] = Field(
        ..., 
        description="List of users"
    )
    total: int = Field(
        ..., 
        description="Total number of users matching the query"
    )
    page: int = Field(
        1, 
        description="Current page number"
    )
    pages: int = Field(
        ..., 
        description="Total number of pages"
    )
    size: int = Field(
        ..., 
        description="Number of items per page"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 123,
                        "username": "johndoe",
                        "display_name": "John D.",
                        "profile_image_url": "https://example.com/profiles/johndoe.jpg",
                        "is_following": True
                    },
                    {
                        "id": 124,
                        "username": "janedoe",
                        "display_name": "Jane D.",
                        "profile_image_url": "https://example.com/profiles/janedoe.jpg",
                        "is_following": False
                    }
                ],
                "total": 2,
                "page": 1,
                "pages": 1,
                "size": 20
            }
        }
    }
