from __future__ import annotations

from typing import Any

from core.tenancy import apply_tenant_filter
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseCRUD[ModelT]:
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model

    async def get(self, session: AsyncSession, tenant_id: Any, obj_id: Any) -> ModelT | None:
        statement = select(self.model).where(self.model.id == obj_id)
        statement = apply_tenant_filter(statement, self.model, tenant_id)
        result = await session.execute(statement)
        return result.scalars().first()

    async def list(
        self,
        session: AsyncSession,
        tenant_id: Any,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ModelT]:
        statement = select(self.model).offset(offset).limit(limit)
        statement = apply_tenant_filter(statement, self.model, tenant_id)
        result = await session.execute(statement)
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, tenant_id: Any, data: dict[str, Any]) -> ModelT:
        payload = dict(data)
        payload["tenant_id"] = tenant_id
        obj = self.model(**payload)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update(
        self,
        session: AsyncSession,
        tenant_id: Any,
        obj_id: Any,
        data: dict[str, Any],
    ) -> ModelT | None:
        update_data = {key: value for key, value in data.items() if key != "tenant_id"}
        statement = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**update_data)
            .returning(self.model)
        )
        statement = apply_tenant_filter(statement, self.model, tenant_id)
        result = await session.execute(statement)
        await session.commit()
        return result.scalars().first()

    async def delete(self, session: AsyncSession, tenant_id: Any, obj_id: Any) -> ModelT | None:
        statement = delete(self.model).where(self.model.id == obj_id).returning(self.model)
        statement = apply_tenant_filter(statement, self.model, tenant_id)
        result = await session.execute(statement)
        await session.commit()
        return result.scalars().first()


class SchemaCRUD[ModelT, CreateSchemaT: BaseModel, UpdateSchemaT: BaseModel](BaseCRUD[ModelT]):
    async def create(self, session: AsyncSession, tenant_id: Any, data: CreateSchemaT) -> ModelT:
        return await super().create(session, tenant_id, data.model_dump())

    async def update(
        self,
        session: AsyncSession,
        tenant_id: Any,
        obj_id: Any,
        data: UpdateSchemaT,
    ) -> ModelT | None:
        return await super().update(session, tenant_id, obj_id, data.model_dump(exclude_unset=True))
