from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy import Delete, Select, Update
from sqlalchemy.orm import InstrumentedAttribute


class TenantScopeError(RuntimeError):
    pass


ModelT = TypeVar("ModelT")


def _get_tenant_column[ModelT](model: type[ModelT]) -> InstrumentedAttribute[Any]:
    if not hasattr(model, "tenant_id"):
        raise TenantScopeError(f"Model {model.__name__} must define tenant_id column")

    tenant_attr = model.tenant_id
    if not isinstance(tenant_attr, InstrumentedAttribute):
        raise TenantScopeError(f"Model {model.__name__} tenant_id must be a mapped column")

    return tenant_attr


def apply_tenant_filter[ModelT](
    statement: Select[Any] | Update | Delete,
    model: type[ModelT],
    tenant_id: Any,
):
    if tenant_id is None:
        raise TenantScopeError("tenant_id is required for tenant-scoped queries")

    tenant_column = _get_tenant_column(model)

    if isinstance(statement, (Select, Update, Delete)):
        return statement.where(tenant_column == tenant_id)

    raise TypeError("Unsupported statement type for tenant scoping")
