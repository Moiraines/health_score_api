"""Authentication and authorization related schemas."""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, constr, validator

from .enums import UserRole, AccountStatus
from ..auth import (
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_REGEX,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

class Token(BaseModel):
    """JWT token response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(
        ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        description="Token expiration time in seconds"
    )
    refresh_token: str = Field(..., description="Refresh token")
    refresh_expires_in: int = Field(
        REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        description="Refresh token expiration time in seconds"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_expires_in": 604800
            }
        }

class TokenData(BaseModel):
    """Data contained in the JWT token."""
    sub: str = Field(..., description="Subject (user ID)")
    scopes: List[str] = Field(
        ["me"], 
        description="List of scopes the token has access to"
    )
    exp: datetime = Field(
        ..., 
        description="Expiration timestamp"
    )
    iat: datetime = Field(
        ..., 
        description="Issued at timestamp"
    )
    jti: str = Field(
        ..., 
        description="JWT ID (unique identifier for the token)"
    )

class UserLogin(BaseModel):
    """User login credentials."""
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Account password")
    remember_me: bool = Field(
        False, 
        description="Whether to remember the user (longer session)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "SecurePass123!",
                "remember_me": True
            }
        }

class UserLoginResponse(BaseModel):
    """Response after successful login."""
    user_id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    role: UserRole = Field(..., description="User's role")
    status: AccountStatus = Field(..., description="Account status")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 123,
                "email": "user@example.com",
                "username": "johndoe",
                "role": "user",
                "status": "active",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

class PasswordResetRequest(BaseModel):
    """Request password reset email."""
    email: EmailStr = Field(..., description="User's email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

class PasswordResetConfirm(BaseModel):
    """Confirm password reset with new password."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., 
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        regex=PASSWORD_REGEX,
        description=f"New password (must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters long, "
                  "contain at least one uppercase letter, one lowercase letter, "
                  "one number, and one special character)"
    )
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "NewSecurePass123!",
                "confirm_password": "NewSecurePass123!"
            }
        }

class EmailVerificationRequest(BaseModel):
    """Request email verification."""
    email: EmailStr = Field(..., description="Email address to verify")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

class EmailVerificationConfirm(BaseModel):
    """Confirm email verification."""
    token: str = Field(..., description="Email verification token")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

class ChangePasswordRequest(BaseModel):
    """Change password while authenticated."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., 
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        regex=PASSWORD_REGEX,
        description=f"New password (must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters long, "
                  "contain at least one uppercase letter, one lowercase letter, "
                  "one number, and one special character)"
    )
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character"
            )
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('new passwords do not match')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewSecurePass123!",
                "confirm_password": "NewSecurePass123!"
            }
        }

class SessionInfo(BaseModel):
    """Information about an active user session."""
    session_id: str = Field(..., description="Unique session ID")
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="IP address")
    created_at: datetime = Field(..., description="When the session was created")
    expires_at: datetime = Field(..., description="When the session expires")
    is_current: bool = Field(False, description="Whether this is the current session")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "ip_address": "192.168.1.1",
                "created_at": "2023-06-08T10:00:00Z",
                "expires_at": "2023-06-15T10:00:00Z",
                "is_current": True
            }
        }

class OAuth2TokenRequest(BaseModel):
    """OAuth2 token request."""
    grant_type: str = Field(..., description="OAuth2 grant type")
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: Optional[str] = Field(None, description="OAuth2 client secret")
    code: Optional[str] = Field(None, description="Authorization code")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "grant_type": "authorization_code",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "code": "authorization-code-here",
                "redirect_uri": "https://your-app.com/callback"
            }
        }
