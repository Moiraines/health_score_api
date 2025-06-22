from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated, Union
from jose import JWTError, jwt
import secrets

from ..schemas.auth import TokenData
from ..schemas.user import User
from ..db.session import get_async_db
from ..core.config import settings

from sqlalchemy.ext.asyncio import AsyncSession



oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.API_V1_STR}/token')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire, 'token_type': 'access'})
    # Add rolling code (simple random string for demo - in production use TOTP or similar)
    to_encode.update({'rolling_code': secrets.token_hex(8)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire, 'token_type': 'refresh'})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("token_type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db = Depends(get_async_db)):
    # Import UserService here to avoid circular imports
    from ..services.user_service import UserService
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get('sub')
        token_type: str = payload.get('token_type')
        if username is None or token_type != 'access':
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user
