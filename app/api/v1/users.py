from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.schemas.user import UserCreate, UserRegisterResponse, UserPrivateResponse
from app.db.models.user import User as UserModel, UserRole
from app.services.user_service import UserService
from app.db.session import get_async_db

router = APIRouter(prefix='/v1', tags=['Users'])

async def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(db)

@router.post('/users/', response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    db_user = await user_service.get_user_by_email(str(user.email))
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')

    # Username uniqueness
    db_username = await user_service.get_user_by_username(user.username)
    if db_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    return await user_service.create_user(user)

@router.get('/users/', response_model=List[UserPrivateResponse])
async def read_users(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(100, ge=1, le=500, description="Page size"),
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_active_user)
):
    if not (current_user.is_superuser or current_user.role == UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    users = await user_service.get_users(skip=skip, limit=limit)
    return users

@router.get('/users/me/', response_model=UserPrivateResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user

@router.get('/users/{user_id}', response_model=UserPrivateResponse)
async def read_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_active_user)
):
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user = await user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
