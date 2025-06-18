"""User-related Pydantic schemas for the Health Score API."""

# Import all schemas to make them available when importing from app.schemas.user
from .enums import (
    Gender,
    ActivityLevel,
    FitnessGoal,
    UserRole,
    AccountStatus,
    NotificationPreference
)

from .base import UserBase
User = UserBase

from .create import (
    UserCreate,
    UserInviteCreate,
    UserRegisterResponse
)

from .update import (
    UserUpdate,
    UserEmailUpdate,
    UserPasswordUpdate,
    UserPreferencesUpdate,
    UserStatusUpdate
)

from .response import (
    UserPublicResponse,
    UserPrivateResponse,
    UserStatsResponse,
    UserSearchResult,
    UserListResponse
)

from .auth import (
    Token,
    TokenData,
    UserLogin,
    UserLoginResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    ChangePasswordRequest,
    SessionInfo,
    OAuth2TokenRequest
)

# Re-export all schemas for easier imports
__all__ = [
    # Enums
    'Gender',
    'ActivityLevel',
    'FitnessGoal',
    'UserRole',
    'AccountStatus',
    'NotificationPreference',
    
    # Base
    'UserBase',
    
    # Create
    'UserCreate',
    'UserInviteCreate',
    'UserRegisterResponse',
    
    # Update
    'UserUpdate',
    'UserEmailUpdate',
    'UserPasswordUpdate',
    'UserPreferencesUpdate',
    'UserStatusUpdate',
    
    # Response
    'UserPublicResponse',
    'UserPrivateResponse',
    'UserStatsResponse',
    'UserSearchResult',
    'UserListResponse',
    
    # Auth
    'Token',
    'TokenData',
    'UserLogin',
    'UserLoginResponse',
    'PasswordResetRequest',
    'PasswordResetConfirm',
    'EmailVerificationRequest',
    'EmailVerificationConfirm',
    'ChangePasswordRequest',
    'SessionInfo',
    'OAuth2TokenRequest'
]
