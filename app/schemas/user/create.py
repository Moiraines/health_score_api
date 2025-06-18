"""Schemas for user creation and registration."""
from typing import Optional
from pydantic import BaseModel, Field, constr, validator, EmailStr

from .base import UserBase, USERNAME_PATTERN, USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH
from ..auth import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_REGEX

class UserCreate(UserBase):
    """Schema for creating a new user (registration)."""
    password: constr(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        pattern=PASSWORD_REGEX
    ) = Field(
        ...,
        description=f"Password must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters long, "
                  "contain at least one uppercase letter, one lowercase letter, one number, "
                  "and one special character",
        example="SecurePass123!"
    )
    password_confirm: str = Field(
        ...,
        description="Password confirmation (must match password)",
        example="SecurePass123!"
    )
    
    # Terms acceptance
    accept_terms: bool = Field(
        ...,
        description="Must be true to accept terms and conditions",
        example=True
    )
    
    # Marketing preferences
    newsletter_subscription: bool = Field(
        False,
        description="Whether to subscribe to the newsletter"
    )
    
    # Validation
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
    
    @validator('accept_terms')
    def must_accept_terms(cls, v):
        if not v:
            raise ValueError('You must accept the terms and conditions')
        return v
    
    class Config:
        schema_extra = {
            **UserBase.Config.schema_extra["example"],
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "accept_terms": True,
            "newsletter_subscription": True
        }

class UserInviteCreate(BaseModel):
    """Schema for inviting a new user (admin only)."""
    email: EmailStr = Field(..., description="Email address of the user to invite")
    role: str = Field(..., description="Role to assign to the user")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "new.user@example.com",
                "role": "user"
            }
        }

class UserRegisterResponse(BaseModel):
    """Response schema after successful user registration."""
    id: int = Field(..., description="Unique user ID")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    message: str = Field(
        "Registration successful. Please check your email to verify your account.",
        description="Status message"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "username": "johndoe",
                "message": "Registration successful. Please check your email to verify your account."
            }
        }
