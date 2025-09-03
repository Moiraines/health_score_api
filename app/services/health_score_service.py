from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.health_record import HealthScore
from ..schemas.health_score import HealthScoreCreate, HealthScoreUpdate

class HealthScoreService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_health_score(self, health_score_id: int) -> Optional[HealthScore]:
        result = await self.db.execute(
            select(HealthScore).where(HealthScore.id == health_score_id)
        )
        return result.scalars().first()

    async def get_health_scores(self, user_id: int, skip: int = 0, limit: int = 100) -> List[HealthScore]:
        result = await self.db.execute(
            select(HealthScore)
            .where(HealthScore.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_health_scores_by_date_range(
        self, 
        user_id: int, 
        start_date: date, 
        end_date: date, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[HealthScore]:
        result = await self.db.execute(
            select(HealthScore)
            .where(
                and_(
                    HealthScore.user_id == user_id,
                    HealthScore.timestamp >= start_date,
                    HealthScore.timestamp <= end_date
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_health_score(self, user_id: int, health_score: HealthScoreCreate) -> HealthScore:
        health_score_data = health_score.model_dump()
        db_health_score = HealthScore(user_id=user_id, **health_score_data)
        
        self.db.add(db_health_score)
        await self.db.commit()
        await self.db.refresh(db_health_score)
        return db_health_score

    async def update_health_score(
        self, 
        health_score_id: int, 
        health_score_update: HealthScoreUpdate
    ) -> Optional[HealthScore]:
        db_health_score = await self.get_health_score(health_score_id)
        if not db_health_score:
            return None
            
        update_data = health_score_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_health_score, key, value)
                
        await self.db.commit()
        await self.db.refresh(db_health_score)
        return db_health_score

    async def delete_health_score(self, health_score_id: int) -> bool:
        db_health_score = await self.get_health_score(health_score_id)
        if not db_health_score:
            return False
            
        await self.db.delete(db_health_score)
        await self.db.commit()
        return True

    async def calculate_average_health_score(self, user_id: int, days: int = 7) -> float:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        health_scores = await self.get_health_scores_by_date_range(
            user_id=user_id,
            start_date=start_date.date(),
            end_date=end_date.date()
        )
        
        if not health_scores:
            return 0.0
        
        total_score = sum(health_score.score for health_score in health_scores)
        return total_score / len(health_scores) if health_scores else 0.0
