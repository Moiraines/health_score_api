from fastapi import Depends
from typing import Optional

from ..db.session import get_db
from ..core.password_utils import verify_password, get_password_hash
from ..db.models.user import User

class AuthService:
    def __init__(self, db=Depends(get_db)):
        self.db = db

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
