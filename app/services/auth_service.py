from fastapi import Depends
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.password_utils import verify_password
from ..db.models.user import User

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
