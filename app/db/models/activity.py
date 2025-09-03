from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any
from datetime import time
from ..base import Base

class ActivityType(str, PyEnum):
    RUNNING = "running"
    WALKING = "walking"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    WEIGHT_TRAINING = "weight_training"
    YOGA = "yoga"
    PILATES = "pilates"
    HIKING = "hiking"
    DANCING = "dancing"
    MARTIAL_ARTS = "martial_arts"
    CROSSFIT = "crossfit"
    ELLIPTICAL = "elliptical"
    ROWING = "rowing"
    STAIR_CLIMBER = "stair_climber"
    OTHER = "other"

class Activity(Base):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Activity Details
    activity_type = Column(Enum(ActivityType), nullable=False)
    custom_activity_name = Column(String, nullable=True)  # For 'other' activity types
    
    # Timing
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # Calculated if not provided
    
    # Metrics
    distance_meters = Column(Float, nullable=True)
    elevation_gain_meters = Column(Float, nullable=True)
    elevation_loss_meters = Column(Float, nullable=True)
    calories_burned = Column(Float, nullable=True)
    average_heart_rate = Column(Integer, nullable=True)  # BPM
    max_heart_rate = Column(Integer, nullable=True)  # BPM
    
    # Intensity
    perceived_exertion = Column(Integer, nullable=True)  # 1-10 scale
    average_power_watts = Column(Float, nullable=True)  # For cycling
    
    # Location and Route
    location = Column(String, nullable=True)  # Free text or specific location
    gps_data = Column(JSON, nullable=True)  # Store GPS coordinates if available
    
    # Additional Details
    notes = Column(String, nullable=True)
    tags = Column(JSON, default=list)  # For categorization
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}', start='{self.start_time}')>"


class WorkoutPlan(Base):
    __tablename__ = 'workout_plans'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Plan Details
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Schedule
    days_of_week = Column(JSON, nullable=False)  # List of days (0-6, where 0 is Monday)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    workouts = relationship("WorkoutPlanExercise", back_populates="plan")
    
    def __repr__(self):
        return f"<WorkoutPlan(id={self.id}, name='{self.name}')>"


class WorkoutPlanExercise(Base):
    __tablename__ = 'workout_plan_exercises'
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey('workout_plans.id'), nullable=False)
    
    # Exercise Details
    exercise_name = Column(String, nullable=False)
    exercise_type = Column(Enum(ActivityType), nullable=False)
    
    # Sets and Reps
    target_sets = Column(Integer, nullable=True)
    target_reps = Column(String, nullable=True)  # Can be a range like '8-12'
    target_weight_kg = Column(Float, nullable=True)
    
    # Duration (for time-based exercises)
    target_duration_seconds = Column(Integer, nullable=True)
    
    # Order in the workout
    sort_order = Column(Integer, nullable=False, default=0)
    
    # Rest time between sets (in seconds)
    rest_time_seconds = Column(Integer, nullable=True)
    
    # Relationships
    plan = relationship("WorkoutPlan", back_populates="workouts")
    
    def __repr__(self):
        return f"<WorkoutPlanExercise(id={self.id}, exercise='{self.exercise_name}')>"
