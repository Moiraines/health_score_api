from typing import List, Optional
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.activity import Activity
from ..schemas.activity import ActivityCreate, ActivityUpdate

class ActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_activity(self, activity_id: int) -> Optional[Activity]:
        result = await self.db.execute(select(Activity).where(Activity.id == activity_id))
        return result.scalars().first()

    async def get_activities(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Activity]:
        result = await self.db.execute(
            select(Activity)
            .where(Activity.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_activities_by_date_range(self, user_id: int, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[Activity]:
        result = await self.db.execute(
            select(Activity)
            .where(Activity.user_id == user_id)
            .where(Activity.timestamp >= start_date)
            .where(Activity.timestamp <= end_date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_activity(self, user_id: int, activity: ActivityCreate) -> Activity:
        db_activity = Activity(user_id=user_id, **activity.model_dump())
        self.db.add(db_activity)
        await self.db.commit()
        await self.db.refresh(db_activity)
        return db_activity

    async def update_activity(self, activity_id: int, activity_update: ActivityUpdate) -> Optional[Activity]:
        db_activity = await self.get_activity(activity_id)
        if db_activity:
            update_data = activity_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:
                    setattr(db_activity, key, value)
            await self.db.commit()
            await self.db.refresh(db_activity)
        return db_activity

    async def delete_activity(self, activity_id: int) -> bool:
        db_activity = await self.get_activity(activity_id)
        if db_activity:
            await self.db.delete(db_activity)
            await self.db.commit()
            return True
        return False

    async def calculate_health_score(self, user_id: int, days: int = 7) -> float:
        # Simple health score calculation based on recent activities
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        activities = await self.get_activities_by_date_range(
            user_id=user_id,
            start_date=start_date.date(),
            end_date=end_date.date()
        )

        if not activities:
            return 0.0

        total_duration = sum(activity.duration_minutes for activity in activities)
        total_calories = sum(activity.calories_burned or 0 for activity in activities)
        activity_count = len(activities)

        # Simple scoring formula (this can be made more sophisticated)
        score = (total_duration / 10.0) + (total_calories / 100.0) + (activity_count * 2.0)
        return min(100.0, score)
