from __future__ import annotations

from uuid import UUID

from core.config import BaseSchema
from core.filters import FilterOperator, JsonbFilter
from pydantic import Field


class CatalogFilterSchema(BaseSchema):
    field: str
    op: FilterOperator
    value: str | int | float | bool | list[str] | list[int] | list[float] | None = None
    value_type: str | None = None
    path: tuple[str, ...] | None = None

    def to_jsonb_filter(self) -> JsonbFilter:
        return JsonbFilter(
            field=self.field,
            op=self.op,
            value=self.value,
            value_type=self.value_type,
            path=self.path,
        )


class CatalogSearchRequest(BaseSchema):
    tenant_id: UUID
    filters: list[CatalogFilterSchema] = Field(default_factory=list)
    logic: str = Field(default="and", pattern="^(and|or)$")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class CatalogProductResponse(BaseSchema):
    id: UUID
    tenant_id: UUID
    name: str
    description: str | None = None
    attributes: dict
