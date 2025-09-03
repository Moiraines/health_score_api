from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from ..base import Base

class HealthMetricType(str, PyEnum):
    """Types of health metrics that can be tracked."""
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_OXYGEN = "blood_oxygen"
    BODY_TEMPERATURE = "body_temperature"
    BODY_WEIGHT = "body_weight"
    BODY_FAT_PERCENTAGE = "body_fat_percentage"
    MUSCLE_MASS = "muscle_mass"
    BMI = "bmi"
    BLOOD_GLUCOSE = "blood_glucose"
    CHOLESTEROL = "cholesterol"
    SLEEP_DURATION = "sleep_duration"
    SLEEP_QUALITY = "sleep_quality"
    STRESS_LEVEL = "stress_level"
    ENERGY_LEVEL = "energy_level"
    MOOD = "mood"
    PAIN_LEVEL = "pain_level"
    STEPS = "steps"
    ACTIVE_MINUTES = "active_minutes"
    WATER_INTAKE = "water_intake"
    CALORIES_BURNED = "calories_burned"
    CALORIES_CONSUMED = "calories_consumed"


class HealthRecord(Base):
    """Comprehensive health record tracking various health metrics over time."""
    __tablename__ = 'health_records'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Core Health Metrics
    metric_type = Column(Enum(HealthMetricType), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)  # e.g., 'bpm', 'mmHg', '°C', 'kg', '%'
    
    # Additional context
    notes = Column(String(500), nullable=True)
    source = Column(String(100), nullable=True)  # e.g., 'manual', 'device_name', 'app_name'
    device_id = Column(String(100), nullable=True)  # If recorded from a device
    
    # Timing
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)  # For metrics over a time period
    
    # Metadata
    is_manual_entry = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)  # 0-1 confidence in the measurement
    raw_data = Column(JSON, nullable=True)  # Store raw data from devices/APIs
    
    # Relationships
    user = relationship("User", back_populates="health_records")
    
    def __repr__(self):
        return f"<HealthRecord(id={self.id}, user_id={self.user_id}, metric='{self.metric_type}', value={self.value}{self.unit or ''})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the record to a dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'metric_type': self.metric_type.value,
            'value': self.value,
            'unit': self.unit,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'notes': self.notes,
            'source': self.source,
            'is_manual_entry': self.is_manual_entry
        }


class HealthScore(Base):
    """Aggregated health score calculated from various health metrics."""
    __tablename__ = 'health_scores'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Score Details
    overall_score = Column(Float, nullable=False)  # 0-100
    category_scores = Column(JSON, nullable=True)  # e.g., {'fitness': 85, 'nutrition': 70, 'sleep': 90}
    
    # Metrics used in calculation
    metrics_considered = Column(JSON, nullable=True)  # List of metric IDs used in calculation
    
    # Timing
    date = Column(Date, nullable=False, index=True)  # The date this score represents
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional context
    notes = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<HealthScore(id={self.id}, user_id={self.user_id}, score={self.overall_score}, date='{self.date}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the score to a dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'overall_score': self.overall_score,
            'category_scores': self.category_scores,
            'date': self.date.isoformat(),
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'notes': self.notes
        }


class HealthGoal(Base):
    """User-defined health and fitness goals."""
    __tablename__ = 'health_goals'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    
    # Goal Details
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    metric_type = Column(Enum(HealthMetricType), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    
    # Goal Period
    start_date = Column(Date, nullable=False, default=func.current_date())
    target_date = Column(Date, nullable=True)
    
    # Progress Tracking
    is_achieved = Column(Boolean, default=False)
    progress_percentage = Column(Float, default=0.0)  # 0-100
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<HealthGoal(id={self.id}, user_id={self.user_id}, name='{self.name}', progress={self.progress_percentage}%)>"
    
    def update_progress(self, current_value: float) -> None:
        """Update the progress percentage based on current value."""
        if self.target_value == 0:
            self.progress_percentage = 0.0
        else:
            self.progress_percentage = min(100.0, (current_value / self.target_value) * 100)
        
        self.current_value = current_value
        self.is_achieved = self.progress_percentage >= 100.0
