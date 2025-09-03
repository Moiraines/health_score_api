"""Schemas for updating user information."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, constr

from .enums import Gender, ActivityLevel, FitnessGoal, NotificationPreference

class UserBaseUpdate(BaseModel):
    """Base update schema for common user fields."""
    # Personal Information
    first_name: Optional[constr(max_length=50)] = Field(
        None, 
        description="User's first name"
    )
    last_name: Optional[constr(max_length=50)] = Field(
        None, 
        description="User's last name"
    )
    date_of_birth: Optional[str] = Field(
        None, 
        description="Date of birth (YYYY-MM-DD)"
    )
    gender: Optional[Gender] = Field(
        None, 
        description="User's gender identity"
    )
    
    # Profile Information
    display_name: Optional[constr(max_length=100)] = Field(
        None, 
        description="User's display name"
    )
    bio: Optional[constr(max_length=500)] = Field(
        None, 
        description="User's biography or description"
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
        None, 
        description="User's preferred language code (ISO 639-1)"
    )
    timezone: Optional[str] = Field(
        None, 
        description="User's timezone (IANA timezone name)"
    )
    measurement_system: Optional[str] = Field(
        None, 
        description="Preferred measurement system (metric/imperial)"
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
        None, 
        description="User's fitness objectives"
    )
    
    # Contact Information
    phone_number: Optional[str] = Field(
        None, 
        description="User's phone number with country code"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
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

class UserEmailUpdate(BaseModel):
    """Schema for updating user email."""
    email: str = Field(..., description="New email address")
    current_password: str = Field(..., description="Current password for verification")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "new.email@example.com",
                "current_password": "CurrentPass123!"
            }
        }

class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., 
        description=f"New password (must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters long, "
                  "contain at least one uppercase letter, one lowercase letter, "
                  "one number, and one special character)"
    )
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('new passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character"
            )
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewSecurePass123!",
                "confirm_password": "NewSecurePass123!"
            }
        }

class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    email_notifications: Optional[bool] = Field(
        None, 
        description="Enable/disable email notifications"
    )
    push_notifications: Optional[bool] = Field(
        None, 
        description="Enable/disable push notifications"
    )
    sms_notifications: Optional[bool] = Field(
        None, 
        description="Enable/disable SMS notifications"
    )
    newsletter_subscription: Optional[bool] = Field(
        None, 
        description="Subscribe/unsubscribe from newsletter"
    )
    dark_mode: Optional[bool] = Field(
        None, 
        description="Enable/disable dark mode"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "email_notifications": True,
                "push_notifications": True,
                "sms_notifications": False,
                "newsletter_subscription": True,
                "dark_mode": True
            }
        }

class UserStatusUpdate(BaseModel):
    """Schema for updating user status (admin only)."""
    status: str = Field(..., description="New account status")
    reason: Optional[str] = Field(
        None, 
        description="Reason for status change"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "suspended",
                "reason": "Violation of terms of service"
            }
        }
