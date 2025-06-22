from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.core.security import get_current_active_user
from app.schemas.activity import Activity, ActivityCreate, ActivityUpdate
from app.schemas.user import User
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
async def create_activity(activity: ActivityCreate, activity_service: ActivityService = Depends(get_activity_service), current_user: User = Depends(get_current_active_user)):
    return await activity_service.create_activity(current_user.id, activity)

@router.get('/activities/', response_model=List[Activity])
async def read_activities(
    date_range: Optional[DateRange] = None, 
    skip: int = 0, 
    limit: int = 100, 
    activity_service: ActivityService = Depends(get_activity_service),
    current_user: User = Depends(get_current_active_user)
):
    if date_range:
        return await activity_service.get_activities_by_date_range(current_user.id, date_range.start_date, date_range.end_date, skip=skip, limit=limit)
    return await activity_service.get_activities(current_user.id, skip=skip, limit=limit)

@router.get('/activities/{activity_id}', response_model=Activity)
async def read_activity(activity_id: int, activity_service: ActivityService = Depends(get_activity_service), current_user: User = Depends(get_current_active_user)):
    activity = await activity_service.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail='Activity not found')
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    return activity

@router.put('/activities/{activity_id}', response_model=Activity)
async def update_activity(activity_id: int, activity_update: ActivityUpdate, activity_service: ActivityService = Depends(get_activity_service), current_user: User = Depends(get_current_active_user)):
    activity = await activity_service.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail='Activity not found')
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    return await activity_service.update_activity(activity_id, activity_update)

@router.delete('/activities/{activity_id}')
async def delete_activity(activity_id: int, activity_service: ActivityService = Depends(get_activity_service), current_user: User = Depends(get_current_active_user)):
    activity = await activity_service.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail='Activity not found')
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    await activity_service.delete_activity(activity_id)
    return {'message': 'Activity deleted successfully'}

@router.get('/activities/calculate-score/', response_model=float)
async def calculate_health_score(days: int = 7, activity_service: ActivityService = Depends(get_activity_service), current_user: User = Depends(get_current_active_user)):
    return await activity_service.calculate_health_score(current_user.id, days)
