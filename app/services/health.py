"""
Health metrics service layer.
"""
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text

from app.crud.base import CRUDBase
from app.db.models.health_record import HealthRecord
from app.schemas import (
    HealthMetricCreate,
    HealthMetricUpdate,
    HealthMetricType,
    HealthMetricAggregation,
)

class HealthMetricService(CRUDBase[HealthRecord, HealthMetricCreate, HealthMetricUpdate]):
    """Health metrics service with CRUD and aggregation operations."""

    async def get_by_user_and_id(
            self,
            db: AsyncSession,
            *,
            id: int,
            user_id: int,
    ) -> Optional[HealthRecord]:
        q = select(self.model).where(
            self.model.id == id,
            self.model.user_id == user_id,
        )
        res = await db.execute(q)
        return res.scalar_one_or_none()

    async def get_by_user_and_type(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int, 
        metric_type: HealthMetricType,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[int, List[HealthRecord]]:
        """Get health metrics for a specific user and type with pagination."""
        query = select(self.model).filter(
            self.model.user_id == user_id,
            self.model.metric_type == metric_type
        ).order_by(self.model.recorded_at.desc())
        
        total = await self.count(db, query=query)
        items = await self.get_multi_query(
            db, 
            query=query.offset(skip).limit(limit)
        )
        return total, items
    
    async def get_latest_by_type(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int, 
        metric_type: HealthMetricType
    ) -> Optional[HealthRecord]:
        """Get the most recent health metric of a specific type for a user."""
        query = select(self.model).filter(
            self.model.user_id == user_id,
            self.model.metric_type == metric_type
        ).order_by(self.model.recorded_at.desc()).limit(1)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_aggregated(
        self,
        db: AsyncSession,
        *,
        metric_type: HealthMetricType,
        aggregation: HealthMetricAggregation = HealthMetricAggregation.DAILY,
        user_id: int,
        recorded_at_ge: Optional[datetime] = None,
        recorded_at_lt: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:

        period = func.date_trunc(aggregation.value, self.model.recorded_at).label("period")

        q = (
            select(
                period,
                func.count().label("count"),
                func.min(self.model.value).label("min_value"),
                func.max(self.model.value).label("max_value"),
                func.avg(self.model.value).label("avg_value"),
                func.percentile_cont(0.5).within_group(self.model.value).label("median_value"),
            )
            .where(
                self.model.user_id == user_id,
                self.model.metric_type == metric_type,
            )
            .group_by(period)
            .order_by(period)
        )

        if recorded_at_ge:
            q = q.where(self.model.recorded_at >= recorded_at_ge)
        if recorded_at_lt:
            q = q.where(self.model.recorded_at < recorded_at_lt)

        res = await db.execute(q)
        rows = res.all()

        return [
            {
                "period": row.period,
                "count": row.count,
                "min": float(row.min_value) if row.min_value is not None else None,
                "max": float(row.max_value) if row.max_value is not None else None,
                "avg": float(row.avg_value) if row.avg_value is not None else None,
                "median": float(row.median_value) if row.median_value is not None else None,
            }
            for row in rows
        ]
    
    async def get_trends(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        metric_type: HealthMetricType,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get trend data for a health metric over a time period.
        
        Returns:
            Dict with trend data including current value, change from previous period,
            and historical data points.
        """
        # Get current value (most recent)
        current = await self.get_latest_by_type(
            db, user_id=user_id, metric_type=metric_type
        )
        
        if not current:
            return {
                "current_value": None,
                "change_percent": None,
                "trend": "no_data",
                "data_points": []
            }
        
        # Get previous period data for comparison
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        prev_start_date = start_date - timedelta(days=days)
        
        # Get historical data points for the chart
        data = await self.get_aggregated(
            db,
            metric_type=metric_type,
            user_id=user_id,
            recorded_at_ge=start_date,
            recorded_at_le=end_date,
            aggregation=HealthMetricAggregation.DAILY
        )
        
        # Calculate trend
        prev_avg = await self._get_average_value(
            db,
            user_id=user_id,
            metric_type=metric_type,
            start_date=prev_start_date,
            end_date=start_date
        )
        
        current_avg = await self._get_average_value(
            db,
            user_id=user_id,
            metric_type=metric_type,
            start_date=start_date,
            end_date=end_date
        )
        
        change_percent = None
        if prev_avg and current_avg and prev_avg != 0:
            change_percent = ((current_avg - prev_avg) / prev_avg) * 100
        
        return {
            "current_value": current.value,
            "current_unit": current.unit,
            "change_percent": change_percent,
            "trend": self._get_trend_direction(change_percent) if change_percent is not None else "neutral",
            "data_points": data
        }
    
    async def _get_average_value(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        metric_type: HealthMetricType,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[float]:
        """Helper method to get average value for a time period."""
        query = select([func.avg(self.model.value)]).filter(
            self.model.user_id == user_id,
            self.model.metric_type == metric_type,
            self.model.recorded_at >= start_date,
            self.model.recorded_at < end_date
        )
        
        result = await db.execute(query)
        return result.scalar()

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        metric_type: Optional[HealthMetricType] = None,
        recorded_at_ge: Optional[datetime] = None,
        recorded_at_le: Optional[datetime] = None,
    ) -> Tuple[int, List[HealthRecord]]:
        filters = [self.model.user_id == user_id]
        if metric_type:
            filters.append(self.model.metric_type == metric_type)
        if recorded_at_ge:
            filters.append(self.model.recorded_at >= recorded_at_ge)
        if recorded_at_le:
            filters.append(self.model.recorded_at < recorded_at_le)

        # ---- TOTAL: COUNT(*) върху същите филтри
        count_q = select(func.count()).select_from(self.model).where(*filters)
        total = (await db.execute(count_q)).scalar_one()

        q = (
            select(self.model)
            .where(*filters)
            .order_by(self.model.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await db.execute(q)
        items = res.scalars().all()

        return total, items

    async def create(
            self,
            db: AsyncSession,
            *,
            obj_in: HealthMetricCreate,
            **kwargs: Any,
    ) -> HealthRecord:
        user_id = kwargs.get("user_id")
        if user_id is None:
            raise ValueError("user_id is required to create HealthRecord")

        data: Dict[str, Any] = obj_in.model_dump(exclude_unset=True)

        record = HealthRecord(
            user_id=user_id,
            metric_type=data["metric_type"],
            value=data["value"],
            unit=data.get("unit"),
            recorded_at=data.get("recorded_at"),
            notes=data.get("notes"),
            source=data.get("source"),
        )

        if data["metric_type"] == HealthMetricType.BLOOD_PRESSURE:
            record.raw_data = {
                "systolic": data.get("systolic"),
                "diastolic": data.get("diastolic"),
            }

        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    async def update(
            self,
            db: AsyncSession,
            *,
            db_obj: HealthRecord,
            obj_in: HealthMetricUpdate,
    ) -> HealthRecord:
        data: Dict[str, Any] = obj_in.model_dump(exclude_unset=True)

        if db_obj.metric_type == HealthMetricType.BLOOD_PRESSURE:
            systolic = data.get("systolic")
            diastolic = data.get("diastolic")
            if systolic is None or diastolic is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="For blood_pressure you must provide both 'systolic' and 'diastolic'.",
                )
            raw = dict(db_obj.raw_data or {})
            raw["systolic"] = int(systolic)
            raw["diastolic"] = int(diastolic)
            db_obj.raw_data = raw
            db_obj.value = 0.0
            if "unit" in data and data["unit"]:
                db_obj.unit = data["unit"]
            elif not db_obj.unit:
                db_obj.unit = "mmHg"
        else:
            if "value" in data:
                db_obj.value = data["value"]
            data.pop("systolic", None)
            data.pop("diastolic", None)

        for field in ("unit", "recorded_at", "notes", "source"):
            if field in data and data[field] is not None:
                setattr(db_obj, field, data[field])

        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def _get_trend_direction(change_percent: float) -> str:
        """Determine trend direction based on percentage change."""
        if change_percent > 5:
            return "up"
        elif change_percent < -5:
            return "down"
        return "neutral"

# Create a singleton instance
health_metric_service = HealthMetricService(HealthRecord)
