from __future__ import annotations

from typing import Literal
from uuid import UUID

from core.filters import FilterOperator, JsonbFilter
from langchain_core.tools import StructuredTool
from models.product import Product
from pydantic import BaseModel, Field
from services.search import search_products
from sqlalchemy.ext.asyncio import AsyncSession


class CatalogFilterInput(BaseModel):
    field: str = Field(description="JSONB attribute key to filter by")
    op: FilterOperator = Field(description="Filter operator")
    value: str | int | float | bool | list[str] | list[int] | list[float] | None = Field(default=None)
    value_type: Literal["string", "number", "bool"] | None = Field(
        default=None,
        description="Optional explicit value type for comparisons",
    )
    path: list[str] | None = Field(default=None, description="Optional nested path inside JSONB attribute")


class CatalogToolInput(BaseModel):
    filters: list[CatalogFilterInput] = Field(default_factory=list, description="Catalog filters to apply")
    logic: Literal["and", "or"] = Field(default="and", description="How to combine filters")
    offset: int = Field(default=0, ge=0, description="Pagination offset")
    limit: int = Field(default=20, ge=1, le=100, description="Max number of products to return")


def serialize_product(product: Product) -> dict[str, object]:
    return {
        "id": str(product.id),
        "tenant_id": str(product.tenant_id),
        "name": product.name,
        "description": product.description,
        "attributes": dict(product.attributes),
    }


def _to_jsonb_filter(item: CatalogFilterInput) -> JsonbFilter:
    return JsonbFilter(
        field=item.field,
        op=item.op,
        value=item.value,
        value_type=None if item.value_type == "string" else item.value_type,
        path=tuple(item.path) if item.path else None,
    )


async def run_catalog_tool(
    session: AsyncSession,
    tenant_id: UUID | str,
    *,
    filters: list[CatalogFilterInput] | None = None,
    logic: Literal["and", "or"] = "and",
    offset: int = 0,
    limit: int = 20,
) -> list[dict[str, object]]:
    jsonb_filters = [_to_jsonb_filter(item) for item in (filters or [])]
    products = await search_products(
        session,
        tenant_id,
        filters=jsonb_filters or None,
        logic=logic,
        offset=offset,
        limit=limit,
    )
    return [serialize_product(product) for product in products]


def build_catalog_tool(session: AsyncSession, tenant_id: UUID | str) -> StructuredTool:
    async def catalog_tool(
        filters: list[CatalogFilterInput] | None = None,
        logic: Literal["and", "or"] = "and",
        offset: int = 0,
        limit: int = 20,
    ) -> list[dict[str, object]]:
        return await run_catalog_tool(
            session,
            tenant_id,
            filters=filters,
            logic=logic,
            offset=offset,
            limit=limit,
        )

    return StructuredTool.from_function(
        coroutine=catalog_tool,
        name="catalog_tool",
        description="Search products in the tenant catalog using JSONB attribute filters.",
        args_schema=CatalogToolInput,
    )
