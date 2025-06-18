import re
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl, field_validator
from pydantic.networks import AnyHttpUrl
from pydantic.types import constr, conint
from app.core.config import settings

# Password validation constants
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 50
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"

class TokenResponse(BaseModel):
    """Response model for token generation"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Type of token")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }

class Token(TokenResponse):
    """Backward-compat alias for auth endpoints."""
    pass

class TokenData(BaseModel):
    """Data structure for token payload"""
    sub: str = Field(..., description="Subject (user ID)")
    type: TokenType = Field(..., description="Token type")
    scopes: List[str] = Field(default_factory=list, description="List of scopes")
    exp: datetime = Field(..., description="Expiration time")
    iat: datetime = Field(default_factory=datetime.utcnow, description="Issued at time")
    jti: str = Field(default_factory=lambda: str(uuid4()), description="JWT ID")
    
    class Config:
        schema_extra = {
            "example": {
                "sub": "user123",
                "type": "access",
                "scopes": ["read", "write"],
                "exp": "2023-12-31T23:59:59Z",
                "iat": "2023-01-01T00:00:00Z",
                "jti": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., min_length=3, max_length=50, description="Username or email")
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH, 
                         description="User password")
    remember_me: bool = Field(False, description="Whether to extend session duration")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "SecurePass123!",
                "remember_me": False
            }
        }

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$',
                         description="Unique username (letters, numbers, and underscores only)")
    password: constr(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        pattern=PASSWORD_REGEX
    ) = Field(..., description=f"Password must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character")
    
    @field_validator('password')
    def validate_password_strength(cls, v: str) -> str:
        """Additional password validation"""
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
        if len(v) > PASSWORD_MAX_LENGTH:
            raise ValueError(f"Password cannot exceed {PASSWORD_MAX_LENGTH} characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c in "@$!%*?&" for c in v):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "newuser",
                "password": "SecurePass123!"
            }
        }

class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str = Field(..., description="Verification token sent to user's email")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset"""
    email: EmailStr = Field(..., description="User's registered email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, 
                             max_length=PASSWORD_MAX_LENGTH,
                             description="New password")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "NewSecurePass123!"
            }
        }

class ChangePassword(BaseModel):
    """Schema for changing password while authenticated"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, 
                            max_length=PASSWORD_MAX_LENGTH,
                            description="New password")
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldSecurePass123!",
                "new_password": "NewSecurePass123!"
            }
        }

class OAuth2TokenResponse(BaseModel):
    """Response model for OAuth2 token endpoint"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "scope": "read write profile",
                "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

class OAuth2TokenRequestForm:
    """Form data for OAuth2 token endpoint"""
    def __init__(
        self,
        grant_type: str = None,
        username: str = None,
        password: str = None,
        scope: str = "",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        code: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split() if scope else []
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.code = code
        self.redirect_uri = redirect_uri
