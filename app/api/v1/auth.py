from fastapi import APIRouter, Depends, HTTPException, status, Response, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, verify_refresh_token
from app.schemas.auth import Token
from app.services.auth_service import AuthService
from app.db.session import get_async_db

router = APIRouter(prefix='/v1', tags=['Auth'])

async def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)

@router.post('/token', response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(data={'sub': user.username})
    refresh_token = create_refresh_token(data={'sub': user.username})
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

@router.post('/refresh', response_model=Token)
async def refresh_token(
    refresh_token: str = Form(...),
    auth_service: AuthService = Depends(get_auth_service)
):
    username = verify_refresh_token(refresh_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user = await auth_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
            headers={'WWW-Authenticate': 'Bearer', 'Content-Type': 'application/json'},
        )
    access_token = create_access_token(data={'sub': user.username})
    new_refresh_token = create_refresh_token(data={'sub': user.username})
    return {
        'access_token': access_token,
        'refresh_token': new_refresh_token,
        'token_type': 'bearer'
    }
