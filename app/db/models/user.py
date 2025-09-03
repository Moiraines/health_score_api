"""Database models for user management and authentication."""
from datetime import datetime, date, timedelta
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any, Type, TypeVar, cast
import uuid

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, Date, Enum, 
    ForeignKey, JSON, Text, BigInteger, Index, ARRAY, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func, expression
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict

from app.core.security import get_password_hash, verify_password
from app.schemas.user.enums import (
    Gender, 
    ActivityLevel, 
    FitnessGoal, 
    UserRole, 
    AccountStatus,
    NotificationPreference
)
from ..base import Base

# Type variable for generic model operations
ModelType = TypeVar("ModelType", bound="User")

class User(Base):
    """User account model with authentication and profile information."""
    
    __tablename__ = 'users'
    __table_args__ = (
        # Add indexes for common query patterns
        Index('ix_users_email_lower', func.lower(Column('email')), unique=True),
        Index('ix_users_username_lower', func.lower(Column('username')), unique=True),
        Index('ix_users_phone_number', 'phone_number', unique=True, postgresql_where=Column('phone_number').isnot(None)),
        {
            'comment': 'Stores user account information and authentication details',
            'postgresql_partition_by': 'HASH (id)'  # For potential partitioning
        }
    )
    
    # ===== Core Fields =====
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment='Primary key',
        autoincrement=True
    )
    uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        index=True,
        comment='Public user identifier for external APIs'
    )
    
    # ===== Authentication =====
    email = Column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False,
        comment='User\'s primary email address (must be unique)'
    )
    email_verified = Column(
        Boolean, 
        default=False, 
        nullable=False,
        server_default=expression.false(),
        comment='Whether the email has been verified'
    )
    phone_number = Column(
        String(20), 
        nullable=True, 
        index=True,
        comment='E.164 formatted phone number with country code (e.g., +1234567890)'
    )
    phone_verified = Column(
        Boolean, 
        default=False, 
        nullable=False,
        server_default=expression.false(),
        comment='Whether the phone number has been verified'
    )
    hashed_password = Column(
        String(255), 
        nullable=True,  # Nullable to support OAuth users
        comment='Argon2 hashed password (nullable for OAuth users)'
    )
    
    # ===== Profile Information =====
    username = Column(
        String(30), 
        unique=True, 
        index=True, 
        nullable=False,
        comment='Unique username (3-30 chars, alphanumeric + underscores)'
    )
    display_name = Column(
        String(100), 
        nullable=True,
        comment='User\'s display name (2-100 chars)'
    )
    first_name = Column(
        String(50), 
        nullable=True,
        comment='User\'s legal first name'
    )
    last_name = Column(
        String(50), 
        nullable=True,
        comment='User\'s legal last name'
    )
    date_of_birth = Column(
        Date, 
        nullable=True,
        comment='User\'s date of birth (YYYY-MM-DD)'
    )
    gender = Column(
        Enum(Gender, name='user_gender'),
        nullable=True,
        comment='User\'s self-identified gender'
    )
    profile_image_url = Column(
        Text,
        nullable=True,
        comment='URL to the user\'s profile image'
    )
    cover_image_url = Column(
        Text,
        nullable=True,
        comment='URL to the user\'s cover image'
    )
    bio = Column(
        Text,
        nullable=True,
        comment='User\'s biography or description (max 500 chars)'
    )
    
    # ===== Settings & Preferences =====
    language = Column(
        String(10), 
        default='en', 
        nullable=False,
        server_default='en',
        comment='Preferred language code (ISO 639-1)'
    )
    timezone = Column(
        String(50), 
        default='UTC', 
        nullable=False,
        server_default='UTC',
        comment='IANA timezone name (e.g., America/New_York)'
    )
    measurement_system = Column(
        String(10), 
        default='metric', 
        nullable=False,
        server_default='metric',
        comment='Preferred measurement system (metric/imperial)'
    )
    notification_preferences = Column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        default=dict,
        server_default='{}',
        comment='User notification preferences as JSON'
    )
    privacy_settings = Column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        default=dict,
        server_default='{}',
        comment='User privacy settings as JSON'
    )
    
    # ===== Fitness Information =====
    height_cm = Column(
        Float, 
        nullable=True,
        comment='Height in centimeters (50-250)'
    )
    weight_kg = Column(
        Float, 
        nullable=True,
        comment='Weight in kilograms (20-500)'
    )
    activity_level = Column(
        Enum(ActivityLevel, name='user_activity_level'),
        nullable=True,
        comment='User\'s typical activity level'
    )
    fitness_goals = Column(
        ARRAY(Enum(FitnessGoal, name='user_fitness_goal')),
        default=list,
        server_default='{}',
        comment='User\'s fitness objectives'
    )
    health_conditions = Column(
        ARRAY(String(100)),
        default=list,
        server_default='{}',
        comment='List of health conditions or considerations'
    )
    
    # ===== Account Status =====
    role = Column(
        Enum(UserRole, name='user_role'),
        default=UserRole.USER,
        nullable=False,
        server_default=UserRole.USER.value,
        comment='User\'s role in the system'
    )
    status = Column(
        Enum(AccountStatus, name='user_status'),
        default=AccountStatus.PENDING_VERIFICATION,
        nullable=False,
        server_default=AccountStatus.PENDING_VERIFICATION.value,
        comment='Account status (active, suspended, etc.)'
    )
    is_active = Column(
        Boolean, 
        default=True, 
        nullable=False,
        server_default=expression.true(),
        comment='Soft delete flag'
    )
    is_superuser = Column(
        Boolean, 
        default=False, 
        nullable=False,
        server_default=expression.false(),
        comment='Has superuser privileges'
    )
    
    # ===== Timestamps =====
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=func.now(),
        comment='When the user account was created'
    )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        onupdate=func.now(),
        comment='When the user account was last updated'
    )
    last_login_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment='When the user last logged in'
    )
    last_activity_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='When the user was last active on the platform'
    )
    
    # ===== Relationships =====
    # Authentication
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    # Content
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete-orphan")
    water_intakes = relationship("WaterIntake", back_populates="user", cascade="all, delete-orphan")
    walking_sessions = relationship("WalkingSession", back_populates="user", cascade="all, delete-orphan")
    sleep_records = relationship("SleepRecord", back_populates="user", cascade="all, delete-orphan")
    
    # Social
    followers = relationship(
        "User",
        secondary="user_relationships",
        primaryjoin="UserRelationship.followed_id == User.id",
        secondaryjoin="UserRelationship.follower_id == User.id",
        back_populates="following"
    )
    following = relationship(
        "User",
        secondary="user_relationships",
        primaryjoin="UserRelationship.follower_id == User.id",
        secondaryjoin="UserRelationship.followed_id == User.id",
        back_populates="followers"
    )
    
    # ===== Properties =====
    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def initials(self) -> str:
        """Return the user's initials."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[0].upper() if self.username else '?'
    
    @hybrid_property
    def age(self) -> Optional[int]:
        """Calculate the user's age based on date of birth."""
        if not self.date_of_birth:
            return None
            
        today = date.today()
        age = today.year - self.date_of_birth.year - \
              ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return max(0, age)  # Ensure age is not negative
    
    @age.expression
    def age(cls):
        """SQL expression for calculating age."""
        return func.date_part('year', func.age(func.current_date(), cls.date_of_birth)).cast(Integer)
    
    # ===== Methods =====
    def set_password(self, password: str) -> None:
        """Set a new password for the user."""
        self.hashed_password = get_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify if the provided password matches the stored hash."""
        if not self.hashed_password:
            return False
        return verify_password(password, self.hashed_password)
    
    def update_last_login(self, db: Session) -> None:
        """Update the last login timestamp."""
        self.last_login_at = func.now()
        self.last_activity_at = func.now()
        db.add(self)
        db.commit()
    
    def update_activity(self, db: Session) -> None:
        """Update the last activity timestamp."""
        self.last_activity_at = func.now()
        db.add(self)
        db.commit()
    
    def is_following(self, user: 'User') -> bool:
        """Check if this user is following another user."""
        return user in self.following
    
    def follow(self, user: 'User', db: Session) -> None:
        """Follow another user."""
        if not self.is_following(user):
            self.following.append(user)
            db.add(self)
            db.commit()
    
    def unfollow(self, user: 'User', db: Session) -> None:
        """Unfollow a user."""
        if self.is_following(user):
            self.following.remove(user)
            db.add(self)
            db.commit()
    
    def get_notification_preference(self, notification_type: str, default: bool = True) -> bool:
        """Get user's preference for a specific notification type."""
        return self.notification_preferences.get(notification_type, default)
    
    def set_notification_preference(self, notification_type: str, enabled: bool) -> None:
        """Set user's preference for a specific notification type."""
        self.notification_preferences[notification_type] = enabled
    
    # ===== Class Methods =====
    @classmethod
    def get_by_email(cls, db: Session, email: str) -> Optional['User']:
        """Get a user by email (case-insensitive)."""
        return db.query(cls).filter(func.lower(cls.email) == email.lower()).first()
    
    @classmethod
    def get_by_username(cls, db: Session, username: str) -> Optional['User']:
        """Get a user by username (case-insensitive)."""
        return db.query(cls).filter(func.lower(cls.username) == username.lower()).first()
    
    @classmethod
    def get_by_phone(cls, db: Session, phone_number: str) -> Optional['User']:
        """Get a user by phone number."""
        return db.query(cls).filter(cls.phone_number == phone_number).first()
    
    @classmethod
    def authenticate(
        cls, 
        db: Session, 
        identifier: str, 
        password: str
    ) -> Optional['User']:
        """
        Authenticate a user by email/username and password.
        
        Args:
            db: Database session
            identifier: Email or username
            password: Plain text password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        # Try to find user by email or username
        user = cls.get_by_email(db, identifier) or cls.get_by_username(db, identifier)
        if not user:
            return None
            
        # Check if password is correct
        if not user.verify_password(password):
            return None
            
        # Check if account is active
        if not user.is_active or user.status != AccountStatus.ACTIVE:
            return None
            
        return user
    
    # ===== Serialization =====
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user object to dictionary."""
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'email_verified': self.email_verified,
            'phone_number': self.phone_number if include_sensitive else None,
            'phone_verified': self.phone_verified,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'display_name': self.display_name,
            'full_name': self.full_name,
            'initials': self.initials,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,
            'gender': self.gender.value if self.gender else None,
            'profile_image_url': self.profile_image_url,
            'cover_image_url': self.cover_image_url,
            'bio': self.bio,
            'language': self.language,
            'timezone': self.timezone,
            'measurement_system': self.measurement_system,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'activity_level': self.activity_level.value if self.activity_level else None,
            'fitness_goals': [goal.value for goal in self.fitness_goals] if self.fitness_goals else [],
            'health_conditions': self.health_conditions,
            'role': self.role.value,
            'status': self.status.value,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None
        }
        
        if include_sensitive:
            data.update({
                'notification_preferences': dict(self.notification_preferences),
                'privacy_settings': dict(self.privacy_settings)
            })
            
        return data
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserRelationship(Base):
    """Model for tracking relationships between users (following/followers)."""
    __tablename__ = 'user_relationships'
    
    follower_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE'), 
        primary_key=True,
        comment='User who is following'
    )
    followed_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE'), 
        primary_key=True,
        comment='User who is being followed'
    )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        comment='When the relationship was created'
    )
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id])
    followed = relationship("User", foreign_keys=[followed_id])
    
    # Constraints
    __table_args__ = (
        # Prevent self-follows
        # Check('follower_id != followed_id', name='no_self_follow'),
        # Add a unique constraint on the pair
        UniqueConstraint('follower_id', 'followed_id', name='uq_follower_followed'),
        {
            'comment': 'Tracks follower/following relationships between users'
        }
    )
    
    def __repr__(self) -> str:
        return f"<UserRelationship(follower_id={self.follower_id}, followed_id={self.followed_id})>"


class HealthRecord(Base):
    __tablename__ = 'health_records'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Health Metrics
    heart_rate = Column(Integer, nullable=True)  # BPM
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    blood_oxygen = Column(Float, nullable=True)  # SpO2 percentage
    body_temperature = Column(Float, nullable=True)  # Celsius
    
    # Body Composition
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    
    # Health Score
    health_score = Column(Integer, nullable=True)  # 0-100
    
    # Metadata
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="health_records")
    
    def __repr__(self):
        return f"<HealthRecord(id={self.id}, user_id={self.user_id}, score={self.health_score})>"
