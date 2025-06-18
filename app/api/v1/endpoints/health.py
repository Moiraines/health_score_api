"""
Health metrics API endpoints.
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.db.models.user import User
from app.schemas import (
    HealthMetricCreate,
    HealthMetricUpdate,
    HealthMetricResponse,
    HealthMetricListResponse,
    HealthMetricType,
    HealthMetricAggregation,
    HealthMetricAggregationResponse
)
from app.services.health import health_metric_service

router = APIRouter()

@router.post(
    "/metrics",
    response_model=HealthMetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new health metric"
)
async def create_health_metric(
    metric_in: HealthMetricCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new health metric record.
    
    - **value**: The numeric value of the metric
    - **metric_type**: Type of health metric (e.g., heart_rate, blood_pressure)
    - **unit**: Unit of measurement (e.g., bpm, mmHg, kg)
    - **recorded_at**: When the measurement was taken (defaults to now)
    - **notes**: Optional notes about the measurement
    """
    return await health_metric_service.create(db, obj_in=metric_in, user_id=current_user.id)

@router.get(
    "/metrics/{metric_id}",
    response_model=HealthMetricResponse,
    summary="Get a specific health metric by ID"
)
async def get_health_metric(
    metric_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific health metric by its ID.
    """
    metric = await health_metric_service.get(db, id=metric_id, user_id=current_user.id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health metric not found"
        )
    return metric

@router.get(
    "/metrics",
    response_model=HealthMetricListResponse,
    summary="List health metrics with filtering"
)
async def list_health_metrics(
    skip: int = 0,
    limit: int = 100,
    metric_type: Optional[HealthMetricType] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List health metrics with optional filtering by type and date range.
    """
    filters = {"user_id": current_user.id}
    if metric_type:
        filters["metric_type"] = metric_type
    if start_date:
        filters["recorded_at_ge"] = datetime.combine(start_date, datetime.min.time())
    if end_date:
        filters["recorded_at_le"] = datetime.combine(end_date, datetime.max.time())
    
    total, items = await health_metric_service.get_multi(
        db, skip=skip, limit=limit, **filters
    )
    
    return {"total": total, "items": items}

@router.get(
    "/metrics/types/{metric_type}/aggregate",
    response_model=HealthMetricAggregationResponse,
    summary="Get aggregated health metrics"
)
async def aggregate_health_metrics(
    metric_type: HealthMetricType,
    aggregation: HealthMetricAggregation = HealthMetricAggregation.DAILY,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated health metrics data for a specific metric type.
    
    Supports different aggregation levels (daily, weekly, monthly) and
    returns statistics like min, max, avg, and count for each period.
    """
    filters = {
        "user_id": current_user.id,
        "metric_type": metric_type
    }
    
    if start_date:
        filters["recorded_at_ge"] = datetime.combine(start_date, datetime.min.time())
    if end_date:
        filters["recorded_at_le"] = datetime.combine(end_date, datetime.max.time())
    
    results = await health_metric_service.get_aggregated(
        db,
        metric_type=metric_type,
        aggregation=aggregation,
        **filters
    )
    
    return {
        "metric_type": metric_type,
        "aggregation": aggregation,
        "data": results
    }

@router.put(
    "/metrics/{metric_id}",
    response_model=HealthMetricResponse,
    summary="Update a health metric"
)
async def update_health_metric(
    metric_id: int,
    metric_in: HealthMetricUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing health metric.
    """
    metric = await health_metric_service.get(db, id=metric_id, user_id=current_user.id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health metric not found"
        )
    return await health_metric_service.update(db, db_obj=metric, obj_in=metric_in)

@router.delete(
    "/metrics/{metric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a health metric"
)
async def delete_health_metric(
    metric_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a health metric.
    """
    metric = await health_metric_service.get(db, id=metric_id, user_id=current_user.id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health metric not found"
        )
    await health_metric_service.remove(db, id=metric_id)
    return None
