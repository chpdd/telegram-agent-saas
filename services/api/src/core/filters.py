from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from sqlalchemy import and_, cast, or_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import ColumnElement
from sqlalchemy.types import Boolean, Numeric


class FilterError(ValueError):
    pass


class FilterOperator(StrEnum):
    EQ = "eq"
    NEQ = "neq"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    CONTAINS = "contains"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    IS_NULL = "is_null"
    ILIKE = "ilike"


@dataclass(frozen=True)
class JsonbFilter:
    field: str
    op: FilterOperator
    value: Any | None = None
    value_type: str | None = None
    path: tuple[str, ...] | None = None


def _jsonb_path(column: ColumnElement[Any], field: str, path: tuple[str, ...] | None) -> ColumnElement[Any]:
    keys: Iterable[str] = (field,) if not path else (field, *path)
    expr = column
    for key in keys:
        expr = expr[key]
    return expr


def _cast_value(expr: ColumnElement[Any], value_type: str | None) -> ColumnElement[Any]:
    if value_type is None:
        return expr.astext
    if value_type == "number":
        return cast(expr.astext, Numeric)
    if value_type == "bool":
        return cast(expr.astext, Boolean)
    return expr.astext


def _build_filter(column: ColumnElement[JSONB], item: JsonbFilter) -> ColumnElement[bool]:
    if not item.field:
        raise FilterError("Filter field is required")

    op = item.op
    expr = _jsonb_path(column, item.field, item.path)

    if op == FilterOperator.EXISTS:
        if item.path:
            raise FilterError("EXISTS only supports top-level keys")
        return column.has_key(item.field)  # noqa: S608

    if op == FilterOperator.IS_NULL:
        return expr.is_(None)

    value_expr = _cast_value(expr, item.value_type)

    if op == FilterOperator.EQ:
        return value_expr == item.value
    if op == FilterOperator.NEQ:
        return value_expr != item.value
    if op == FilterOperator.LT:
        return value_expr < item.value
    if op == FilterOperator.LTE:
        return value_expr <= item.value
    if op == FilterOperator.GT:
        return value_expr > item.value
    if op == FilterOperator.GTE:
        return value_expr >= item.value
    if op == FilterOperator.ILIKE:
        return value_expr.ilike(item.value)
    if op == FilterOperator.CONTAINS:
        return column.contains(item.value)
    if op == FilterOperator.IN:
        if not isinstance(item.value, (list, tuple, set)):
            raise FilterError("IN operator expects a list-like value")
        return value_expr.in_(list(item.value))
    if op == FilterOperator.NOT_IN:
        if not isinstance(item.value, (list, tuple, set)):
            raise FilterError("NOT_IN operator expects a list-like value")
        return ~value_expr.in_(list(item.value))

    raise FilterError(f"Unsupported operator: {op}")


def build_jsonb_filters(
    column: ColumnElement[JSONB],
    filters: Iterable[JsonbFilter],
    *,
    logic: str = "and",
) -> ColumnElement[bool]:
    clauses = [_build_filter(column, item) for item in filters]
    if not clauses:
        raise FilterError("At least one filter is required")

    if logic == "and":
        return and_(*clauses)
    if logic == "or":
        return or_(*clauses)

    raise FilterError("logic must be 'and' or 'or'")
