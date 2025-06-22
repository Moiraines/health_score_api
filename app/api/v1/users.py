from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.schemas.user import User, UserCreate
from app.services.user_service import UserService
from app.db.session import get_async_db

router = APIRouter(prefix='/v1', tags=['Users'])

async def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(db)

@router.post('/users/', response_model=User)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    db_user = await user_service.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    return await user_service.create_user(user)

@router.get('/users/', response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail='Not authorized')
    users = await user_service.get_users(skip=skip, limit=limit)
    return users

@router.get('/users/me/', response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get('/users/{user_id}', response_model=User)
async def read_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail='Not authorized')
    user = await user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user
