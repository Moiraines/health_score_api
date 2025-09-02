from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.core.security import get_current_active_user
from app.schemas.activity import Activity, ActivityCreate, ActivityUpdate
from app.db.models.user import User as UserModel
from app.services.activity_service import ActivityService

router = APIRouter(prefix='/v1', tags=['Activities'])

async def get_activity_service(
    db: AsyncSession = Depends(get_async_db),
) -> ActivityService:
    return ActivityService(db)

class DateRange(BaseModel):
    start_date: date
    end_date: date

@router.post('/activities/', response_model=Activity)
async def create_activity(activity: ActivityCreate, activity_service: ActivityService = Depends(get_activity_service), current_user: UserModel = Depends(get_current_active_user)):
    return await activity_service.create_activity(current_user.id, activity)

@router.get('/activities/', response_model=List[Activity])
async def read_activities(
    start_date: Optional[date] = Query(None, description="Filter from this date (inclusive)"),
    end_date: Optional[date]   = Query(None, description="Filter to this date (inclusive)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    activity_service: ActivityService = Depends(get_activity_service),
    current_user: UserModel = Depends(get_current_active_user),
):
    if (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide both start_date and end_date, or neither."
        )

    if start_date and end_date:
        return await activity_service.get_activities_by_date_range(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
        )

    return await activity_service.get_activities(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

@router.get('/activities/{activity_id}', response_model=Activity)
async def read_activity(activity_id: int, activity_service: ActivityService = Depends(get_activity_service), current_user: UserModel = Depends(get_current_active_user)):
    activity = await activity_service.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail='Activity not found')
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    return activity

@router.put('/activities/{activity_id}', response_model=Activity)
async def update_activity(activity_id: int, activity_update: ActivityUpdate, activity_service: ActivityService = Depends(get_activity_service), current_user: UserModel = Depends(get_current_active_user)):
    activity = await activity_service.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail='Activity not found')
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    return await activity_service.update_activity(activity_id, activity_update)

@router.delete('/activities/{activity_id}')
async def delete_activity(activity_id: int, activity_service: ActivityService = Depends(get_activity_service), current_user: UserModel = Depends(get_current_active_user)):
    activity = await activity_service.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail='Activity not found')
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    await activity_service.delete_activity(activity_id)
    return {'message': 'Activity deleted successfully'}

@router.get('/activities/calculate-score/', response_model=float)
async def calculate_health_score(days: int = 7, activity_service: ActivityService = Depends(get_activity_service), current_user: UserModel = Depends(get_current_active_user)):
    return await activity_service.calculate_health_score(current_user.id, days)
