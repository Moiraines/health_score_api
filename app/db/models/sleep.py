from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Boolean, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from typing import Optional, List
from datetime import time
from ..base import Base

class SleepStage(str, PyEnum):
    AWAKE = "awake"
    LIGHT = "light"
    DEEP = "deep"
    REM = "rem"
    OUT_OF_BED = "out_of_bed"

class SleepRecord(Base):
    __tablename__ = 'sleep_records'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Sleep Timing
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String, default='UTC')
    
    # Sleep Quality Metrics
    sleep_score = Column(Integer, nullable=True)  # 0-100
    sleep_efficiency = Column(Float, nullable=True)  # Percentage
    total_sleep_minutes = Column(Integer, nullable=True)
    awake_minutes = Column(Integer, nullable=True)
    light_sleep_minutes = Column(Integer, nullable=True)
    deep_sleep_minutes = Column(Integer, nullable=True)
    rem_sleep_minutes = Column(Integer, nullable=True)
    
    # Sleep Latency and Interruptions
    sleep_latency_minutes = Column(Integer, nullable=True)  # Time to fall asleep
    sleep_interruptions = Column(Integer, default=0)  # Number of times woken up
    
    # Sleep Environment
    environment_noise_level = Column(Integer, nullable=True)  # 1-10 scale
    room_temperature_c = Column(Float, nullable=True)
    room_humidity = Column(Float, nullable=True)  # Percentage
    
    # Pre-Sleep Factors
    caffeine_intake_hours_before = Column(Float, nullable=True)
    alcohol_consumption = Column(Boolean, default=False)
    stress_level = Column(Integer, nullable=True)  # 1-10 scale
    
    # Device Data
    device_name = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)  # For storing raw data from wearables
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sleep_records")
    sleep_stages = relationship(
        "SleepStageEntry",
        back_populates="sleep_record",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<SleepRecord(id={self.id}, user_id={self.user_id}, start='{self.start_time}', end='{self.end_time}')>"


class SleepStageEntry(Base):
    __tablename__ = 'sleep_stage_entries'
    
    id = Column(Integer, primary_key=True, index=True)
    sleep_record_id = Column(Integer, ForeignKey('sleep_records.id'), index=True, nullable=False)
    
    # Stage Details
    stage = Column(Enum(SleepStage), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    
    # Relationships
    sleep_record = relationship("SleepRecord", back_populates="sleep_stages")
    
    def __repr__(self):
        return f"<SleepStageEntry(id={self.id}, stage='{self.stage}', duration={self.duration_seconds}s)>"


class SleepGoal(Base):
    __tablename__ = 'sleep_goals'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, unique=True, nullable=False)
    
    # Goal Settings
    target_sleep_duration_minutes = Column(Integer, default=480)  # 8 hours by default
    target_bedtime = Column(String, default="22:00")  # Target bedtime (24h format)
    target_wakeup_time = Column(String, default="06:00")  # Target wakeup time (24h format)
    
    # Notification Preferences
    bedtime_reminder_enabled = Column(Boolean, default=True)
    bedtime_reminder_minutes_before = Column(Integer, default=30)  # Remind 30 mins before target
    wakeup_reminder_enabled = Column(Boolean, default=True)
    
    # Ideal Sleep Window
    ideal_sleep_start = Column(String, nullable=True)  # e.g., "21:00-23:00"
    ideal_sleep_end = Column(String, nullable=True)    # e.g., "05:00-07:00"
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<SleepGoal(user_id={self.user_id}, target={self.target_sleep_duration_minutes//60}h{self.target_sleep_duration_minutes%60}m)>"
