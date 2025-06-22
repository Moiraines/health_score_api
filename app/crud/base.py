# app/crud/base.py
from typing import Generic, TypeVar, Type, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    # ---------- READ ----------
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi_query(self, db: AsyncSession, query):
        res = await db.execute(query)
        return res.scalars().all()

    async def count(self, db: AsyncSession, query=None) -> int:
        stmt = query if query is not None else select(func.count()).select_from(self.model)
        res = await db.execute(stmt)
        return res.scalar_one()

    # ---------- CREATE ----------
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # ---------- UPDATE ----------
    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # ---------- DELETE ----------
    async def remove(self, db: AsyncSession, *, id: int) -> bool:
        result = await db.execute(delete(self.model).where(self.model.id == id))
        await db.commit()
        return result.rowcount > 0
