"""
Health metrics API endpoints.
"""
from datetime import date, datetime, time, timedelta, timezone
from typing import  Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_async_db
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

router = APIRouter(prefix='/v1', tags=['Health Metrics'])

@router.post(
    "/metrics",
    response_model=HealthMetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new health metric"
)
async def create_health_metric(
    metric_in: HealthMetricCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
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
    db: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve a specific health metric by its ID.
    """
    metric = await health_metric_service.get_by_user_and_id(db, id=metric_id, user_id=current_user.id)
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
    db: AsyncSession = Depends(get_async_db),
):
    if (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(status_code=400, detail="Provide both start_date and end_date, or neither.")

    recorded_at_ge = None
    recorded_at_lt = None

    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="start_date cannot be after end_date.")
        recorded_at_ge = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        recorded_at_lt = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)

    total, items = await health_metric_service.get_multi_filtered(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        metric_type=metric_type,
        recorded_at_ge=recorded_at_ge,
        recorded_at_le=recorded_at_lt,
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
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get aggregated health metrics data for a specific metric type.

    Supports different aggregation levels (daily, weekly, monthly) and
    returns statistics like min, max, avg, and count for each period.
    """
    if metric_type == HealthMetricType.BLOOD_PRESSURE:
        raise HTTPException(status_code=400, detail="Aggregation for blood_pressure is not supported yet.")

    if (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(status_code=400, detail="Provide both start_date and end_date, or neither.")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date.")

    recorded_at_ge = None
    recorded_at_lt = None
    if start_date and end_date:
        recorded_at_ge = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        recorded_at_lt = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)

    results = await health_metric_service.get_aggregated(
        db,
        metric_type=metric_type,
        aggregation=aggregation,
        user_id=current_user.id,
        recorded_at_ge=recorded_at_ge,
        recorded_at_lt=recorded_at_lt,
    )

    return {
        "metric_type": metric_type,
        "aggregation": aggregation,
        "data": results,
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
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update an existing health metric.
    """
    metric = await health_metric_service.get_by_user_and_id(db, id=metric_id, user_id=current_user.id)
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
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete a health metric.
    """
    metric = await health_metric_service.get_by_user_and_id(db, id=metric_id, user_id=current_user.id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health metric not found"
        )
    await health_metric_service.remove(db, id=metric_id)
    return {'message': 'Health metric deleted successfully'}
