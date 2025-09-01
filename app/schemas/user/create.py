"""Schemas for user creation and registration."""
from pydantic import BaseModel, Field, constr, field_validator, EmailStr

from ..auth import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_REGEX

USERNAME_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_]*$'  # Must start with a letter
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30

class UserCreate(BaseModel):
    """Schema for creating a new user (registration)."""
    email: EmailStr = Field(..., description="User's unique email address")
    username: constr(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        pattern=USERNAME_PATTERN
    ) = Field(..., description="Unique username (letters, numbers, and underscores only, starting with a letter)")
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
    @field_validator("username")
    def username_lower(cls, v: str) -> str:
        return v.lower()

    @field_validator("email", mode="before")
    def email_lower(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('password_confirm')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('passwords do not match')
        return v

    @field_validator('accept_terms')
    def must_accept_terms(cls, v):
        if not v:
            raise ValueError('You must accept the terms and conditions')
        return v

    model_config = {
        "json_schema_extra": {
            "email": "user@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "accept_terms": True,
            "newsletter_subscription": True
        }
    }

class UserInviteCreate(BaseModel):
    """Schema for inviting a new user (admin only)."""
    email: EmailStr = Field(..., description="Email address of the user to invite")
    role: str = Field(..., description="Role to assign to the user")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "new.user@example.com",
                "role": "user"
            }
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

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "username": "johndoe",
                "message": "Registration successful. Please check your email to verify your account."
            }
        }
    }
