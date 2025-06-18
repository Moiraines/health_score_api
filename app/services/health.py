"""
Health metrics service layer.
"""
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple

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
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated health metrics data.
        
        Args:
            db: Database session
            metric_type: Type of health metric to aggregate
            aggregation: Aggregation level (daily, weekly, monthly)
            **filters: Additional filters (e.g., user_id, date ranges)
            
        Returns:
            List of aggregated data points with statistics
        """
        # Base query
        query = select([
            func.date_trunc(aggregation.value, self.model.recorded_at).label("period"),
            func.count().label("count"),
            func.min(self.model.value).label("min_value"),
            func.max(self.model.value).label("max_value"),
            func.avg(self.model.value).label("avg_value"),
            func.percentile_cont(0.5).within_group(self.model.value).label("median_value"),
        ]).group_by("period").order_by("period")
        
        # Apply filters
        if "user_id" in filters:
            query = query.filter(self.model.user_id == filters["user_id"])
        if "recorded_at_ge" in filters:
            query = query.filter(self.model.recorded_at >= filters["recorded_at_ge"])
        if "recorded_at_le" in filters:
            query = query.filter(self.model.recorded_at <= filters["recorded_at_le"])
        
        # Always filter by metric type
        query = query.filter(self.model.metric_type == metric_type)
        
        # Execute query
        result = await db.execute(query)
        rows = result.all()
        
        # Format results
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
