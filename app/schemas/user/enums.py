"""Enumerations for user-related models."""
from enum import Enum

class Gender(str, Enum):
    """User's gender identity."""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class ActivityLevel(str, Enum):
    """User's activity level for fitness calculations."""
    SEDENTARY = "sedentary"  # Little or no exercise
    LIGHTLY_ACTIVE = "lightly_active"  # Light exercise/sports 1-3 days/week
    MODERATELY_ACTIVE = "moderately_active"  # Moderate exercise/sports 3-5 days/week
    VERY_ACTIVE = "very_active"  # Hard exercise/sports 6-7 days a week
    EXTRA_ACTIVE = "extra_active"  # Very hard exercise & physical job or 2x training

class FitnessGoal(str, Enum):
    """User's primary fitness objectives."""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    GENERAL_FITNESS = "general_fitness"
    SPORT_SPECIFIC = "sport_specific"
    REHABILITATION = "rehabilitation"

class UserRole(str, Enum):
    """User's role in the system."""
    USER = "user"
    COACH = "coach"
    ADMIN = "admin"
    STAFF = "staff"

class AccountStatus(str, Enum):
    """Status of the user's account."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    DELETED = "deleted"

class NotificationPreference(str, Enum):
    """User's notification preferences."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    NONE = "none"
