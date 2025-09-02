from typing import List, Optional
from datetime import date, datetime, timedelta, time

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
            .order_by(Activity.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_activities_by_date_range(self, user_id: int, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[Activity]:
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        result = await self.db.execute(
            select(Activity)
            .where(Activity.user_id == user_id)
            .where(Activity.start_time >= start_dt)
            .where(Activity.start_time <= end_dt)
            .order_by(Activity.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_activity(self, user_id: int, activity: ActivityCreate) -> Activity:

        duration_minutes: Optional[int] = None
        if activity.end_time and activity.start_time:
            delta = activity.end_time - activity.start_time
            duration_minutes = max(0, int(delta.total_seconds() // 60))
        else:
            m = activity.metrics
            dur_sec = getattr(m, "duration_seconds", None) if m is not None else None
            if dur_sec is not None:
                duration_minutes = int(max(0, dur_sec) // 60)

        m = activity.metrics
        db_activity = Activity(
            user_id=user_id,
            activity_type=activity.activity_type,
            custom_activity_name=activity.name,
            notes=activity.description,
            start_time=activity.start_time,
            end_time=activity.end_time,
            duration_minutes=duration_minutes,
            distance_meters=getattr(m, "distance_meters", None) if m else None,
            elevation_gain_meters=getattr(m, "elevation_gain", None) if m else None,
            elevation_loss_meters=getattr(m, "elevation_loss", None) if m else None,
            calories_burned=getattr(m, "calories_burned", None) if m else None,
            average_heart_rate=getattr(m, "heart_rate_avg", None) if m else None,
            max_heart_rate=getattr(m, "heart_rate_max", None) if m else None,
        )

        self.db.add(db_activity)
        await self.db.commit()
        await self.db.refresh(db_activity)
        return db_activity

    async def update_activity(self, activity_id: int, activity_update: ActivityUpdate) -> Optional[Activity]:
        db_activity = await self.get_activity(activity_id)
        if not db_activity:
            return None

        update_data = activity_update.model_dump(exclude_unset=True)

        for key, value in list(update_data.items()):
            if key == "metrics":
                continue  # handle below
            setattr(db_activity, key, value)

        m = update_data.get("metrics")
        if m:
            if m.get("duration_seconds") is not None:
                db_activity.duration_minutes = int(max(0, m["duration_seconds"]) // 60)
            if m.get("distance_meters") is not None:
                db_activity.distance_meters = m["distance_meters"]
            if m.get("elevation_gain") is not None:
                db_activity.elevation_gain_meters = m["elevation_gain"]
            if m.get("elevation_loss") is not None:
                db_activity.elevation_loss_meters = m["elevation_loss"]
            if m.get("calories_burned") is not None:
                db_activity.calories_burned = m["calories_burned"]
            if m.get("heart_rate_avg") is not None:
                db_activity.average_heart_rate = m["heart_rate_avg"]
            if m.get("heart_rate_max") is not None:
                db_activity.max_heart_rate = m["heart_rate_max"]

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
