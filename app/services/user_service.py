from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.password_utils import get_password_hash

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_user(self, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            disabled=False,
            is_admin=False
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = await self.get_user(user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        if 'password' in update_data and update_data['password']:
            update_data['hashed_password'] = get_password_hash(update_data['password'])
            del update_data['password']

        for key, value in update_data.items():
            if value is not None:
                setattr(db_user, key, value)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: int) -> bool:
        db_user = await self.get_user(user_id)
        if not db_user:
            return False

        await self.db.delete(db_user)
        await self.db.commit()
        return True
