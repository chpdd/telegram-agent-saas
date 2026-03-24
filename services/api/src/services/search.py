from __future__ import annotations

from collections.abc import Iterable

from core.filters import JsonbFilter, build_jsonb_filters
from core.tenancy import apply_tenant_filter
from models.product import Product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def search_products(
    session: AsyncSession,
    tenant_id: object,
    *,
    filters: Iterable[JsonbFilter] | None = None,
    logic: str = "and",
    offset: int = 0,
    limit: int = 100,
) -> list[Product]:
    statement = select(Product).offset(offset).limit(limit)
    statement = apply_tenant_filter(statement, Product, tenant_id)

    if filters:
        clause = build_jsonb_filters(Product.attributes, filters, logic=logic)
        statement = statement.where(clause)

    result = await session.execute(statement)
    return list(result.scalars().all())
