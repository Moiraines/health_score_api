from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import date, datetime
from typing import Optional, List
from ..base import Base

class WalkingSession(Base):
    __tablename__ = 'walking_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Session Details
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)  # Null for in-progress sessions
    
    # Step Data
    steps = Column(Integer, default=0, nullable=False)
    distance_meters = Column(Float, default=0.0, nullable=False)
    
    # Calorie and Activity Data
    calories_burned = Column(Float, nullable=True)
    active_minutes = Column(Integer, nullable=True)
    
    # Location and Route
    location = Column(String, nullable=True)  # Free text location
    gps_data = Column(JSON, nullable=True)  # Store GPS coordinates if available
    elevation_gain_meters = Column(Float, nullable=True)
    elevation_loss_meters = Column(Float, nullable=True)
    
    # Pace and Speed
    average_pace_seconds_per_km = Column(Float, nullable=True)  # Average pace in seconds per kilometer
    average_speed_kmh = Column(Float, nullable=True)  # Average speed in km/h
    
    # Heart Rate Data
    average_heart_rate = Column(Integer, nullable=True)  # BPM
    max_heart_rate = Column(Integer, nullable=True)  # BPM
    
    # Device Information
    device_name = Column(String, nullable=True)
    is_tracked = Column(Boolean, default=False)  # Whether the session was actively tracked or auto-detected
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="walking_sessions")
    
    def __repr__(self):
        return f"<WalkingSession(id={self.id}, user_id={self.user_id}, steps={self.steps}, start='{self.start_time}')>"


class DailyStepGoal(Base):
    __tablename__ = 'daily_step_goals'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, unique=True, nullable=False)
    
    # Goal Settings
    daily_step_goal = Column(Integer, default=10000, nullable=False)  # Default 10,000 steps
    
    # Notification Preferences
    reminder_enabled = Column(Boolean, default=True)
    reminder_time = Column(String, default="20:00")  # 24-hour format
    
    # Goal Adjustment
    auto_adjust_goal = Column(Boolean, default=False)  # Automatically adjust goal based on performance
    min_goal = Column(Integer, default=5000)  # Minimum step goal
    max_goal = Column(Integer, default=20000)  # Maximum step goal
    
    # Progress Tracking
    current_streak_days = Column(Integer, default=0)  # Consecutive days meeting goal
    best_streak_days = Column(Integer, default=0)  # Best streak achieved
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<DailyStepGoal(user_id={self.user_id}, goal={self.daily_step_goal} steps)>"


class StepRecord(Base):
    __tablename__ = 'step_records'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Record Details
    date = Column(Date, nullable=False, index=True)  # Date of the record
    steps = Column(Integer, default=0, nullable=False)
    distance_meters = Column(Float, default=0.0, nullable=False)
    calories_burned = Column(Float, nullable=True)
    
    # Activity Minutes
    active_minutes = Column(Integer, default=0, nullable=False)
    
    # Hourly Breakdown (stored as JSON for flexibility)
    hourly_steps = Column(JSON, nullable=True)  # {"0": 100, "1": 50, ..., "23": 200}
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User")
    
    class Config:
        orm_mode = True
    
    def __repr__(self):
        return f"<StepRecord(id={self.id}, user_id={self.user_id}, date='{self.date}', steps={self.steps})>"
