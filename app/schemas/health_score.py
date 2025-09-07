from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, Dict, List

class HealthScoreBase(BaseModel):
    overall_score: float
    category_scores: Optional[Dict[str, float]] = None
    metrics_considered: Optional[List[int]] = None
    notes: Optional[str] = None
    date: date

class HealthScoreCreate(HealthScoreBase):
    pass

class HealthScoreUpdate(HealthScoreBase):
    overall_score: Optional[float] = None
    date: Optional[date] = None

class HealthScore(HealthScoreBase):
    id: int
    user_id: int
    calculated_at: Optional[datetime] = None  # ORM: calculated_at
    model_config = ConfigDict(from_attributes=True)
