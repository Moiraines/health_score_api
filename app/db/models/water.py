from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Optional
from ..base import Base

class WaterIntake(Base):
    __tablename__ = 'water_intakes'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Intake Details
    amount_ml = Column(Float, nullable=False)  # Volume in milliliters
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Additional Metadata
    source = Column(String, nullable=True)  # e.g., 'bottle', 'glass', 'app', 'manual'
    notes = Column(String, nullable=True)  # Any additional notes about the intake
    
    # Relationships
    user = relationship("User", back_populates="water_intakes")
    
    def __repr__(self):
        return f"<WaterIntake(id={self.id}, user_id={self.user_id}, amount_ml={self.amount_ml}, timestamp='{self.timestamp}')>"


class WaterIntakeGoal(Base):
    __tablename__ = 'water_intake_goals'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, unique=True, nullable=False)
    
    # Goal Settings
    daily_goal_ml = Column(Float, nullable=False, default=3000.0)  # Default 3L per day
    
    # Notification Preferences
    reminder_enabled = Column(Boolean, default=True)
    reminder_start_time = Column(String, default="08:00")  # 24-hour format
    reminder_end_time = Column(String, default="20:00")    # 24-hour format
    reminder_interval_minutes = Column(Integer, default=60)  # Remind every X minutes
    
    # Last time the user was reminded
    last_reminder_sent = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<WaterIntakeGoal(user_id={self.user_id}, daily_goal_ml={self.daily_goal_ml})>"
