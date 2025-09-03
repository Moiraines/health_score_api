"""Database models for the Health Score API."""

# Import all models to ensure they are registered with SQLAlchemy
from .user import User, UserRelationship
from .auth import UserSession, RefreshToken

# Import other models as they are created
from .activity import Activity
from .health_record import HealthRecord
from .sleep import SleepRecord
from .walking import WalkingSession
from .water import WaterIntake

# Re-export all models for easier imports
__all__ = [
    # Core models
    'User',
    'UserRelationship',
    
    # Auth models
    'UserSession',
    'RefreshToken',
    
    # Domain models
    'Activity',
    'HealthRecord',
    'SleepRecord',
    'WalkingSession',
    'WaterIntake'
]
