from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.schemas.health_score import HealthScore, HealthScoreCreate, HealthScoreUpdate
from app.schemas.user import User
from app.services.health_score_service import HealthScoreService
from app.db.session import get_async_db

router = APIRouter(prefix='/v1', tags=['health-scores'])

class DateRange(BaseModel):
    start_date: date
    end_date: date

async def get_health_score_service(db: AsyncSession = Depends(get_async_db)) -> HealthScoreService:
    return HealthScoreService(db)

@router.post('/health-scores/', response_model=HealthScore, status_code=status.HTTP_201_CREATED)
async def create_health_score(
    health_score: HealthScoreCreate,
    health_score_service: HealthScoreService = Depends(get_health_score_service),
    current_user: User = Depends(get_current_active_user)
):
    return await health_score_service.create_health_score(current_user.id, health_score)

@router.get('/health-scores/', response_model=List[HealthScore])
async def read_health_scores(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    health_score_service: HealthScoreService = Depends(get_health_score_service),
    current_user: User = Depends(get_current_active_user)
):
    if start_date is not None and end_date is not None:
        return await health_score_service.get_health_scores_by_date_range(
            current_user.id, start_date, end_date, skip=skip, limit=limit
        )
    return await health_score_service.get_health_scores(current_user.id, skip=skip, limit=limit)

@router.get('/health-scores/{score_id}', response_model=HealthScore)
async def read_health_score(
    score_id: int,
    health_score_service: HealthScoreService = Depends(get_health_score_service),
    current_user: User = Depends(get_current_active_user)
):
    health_score = await health_score_service.get_health_score(score_id)
    if health_score is None:
        raise HTTPException(status_code=404, detail='Health score not found')
    if health_score.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail='Not authorized')
    return health_score

@router.put('/health-scores/{score_id}', response_model=HealthScore)
async def update_health_score(
    score_id: int,
    health_score_update: HealthScoreUpdate,
    health_score_service: HealthScoreService = Depends(get_health_score_service),
    current_user: User = Depends(get_current_active_user)
):
    health_score = await health_score_service.get_health_score(score_id)
    if health_score is None:
        raise HTTPException(status_code=404, detail='Health score not found')
    if health_score.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail='Not authorized')
    
    updated_health_score = await health_score_service.update_health_score(score_id, health_score_update)
    if updated_health_score is None:
        raise HTTPException(status_code=404, detail='Health score not found')
    return updated_health_score

@router.delete('/health-scores/{score_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_score(
    score_id: int,
    health_score_service: HealthScoreService = Depends(get_health_score_service),
    current_user: User = Depends(get_current_active_user)
):
    health_score = await health_score_service.get_health_score(score_id)
    if health_score is None:
        raise HTTPException(status_code=404, detail='Health score not found')
    if health_score.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail='Not authorized')
    
    success = await health_score_service.delete_health_score(score_id)
    if not success:
        raise HTTPException(status_code=404, detail='Health score not found')
