from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthScoreBase(BaseModel):
    score: float
    notes: Optional[str] = None

class HealthScoreCreate(HealthScoreBase):
    pass

class HealthScoreUpdate(HealthScoreBase):
    score: Optional[float] = None

class HealthScore(HealthScoreBase):
    id: int
    user_id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        orm_mode = True
