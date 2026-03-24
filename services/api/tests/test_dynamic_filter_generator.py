import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from core.filters import FilterError, FilterOperator, JsonbFilter, build_jsonb_filters  # noqa: E402
from models.product import Product  # noqa: E402


def _compiled_sql(statement, *, literal_binds: bool = True):
    return str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": literal_binds},
        )
    )


def test_build_jsonb_filters_eq_and_number():
    filters = [
        JsonbFilter(field="color", op=FilterOperator.EQ, value="red"),
        JsonbFilter(field="weight", op=FilterOperator.GT, value=10, value_type="number"),
    ]

    clause = build_jsonb_filters(Product.attributes, filters)
    stmt = select(Product).where(clause)
    sql = _compiled_sql(stmt, literal_binds=False)

    assert "attributes" in sql
    assert "CAST" in sql
    assert "->>" in sql


def test_build_jsonb_filters_contains_and_in():
    filters = [
        JsonbFilter(field="tags", op=FilterOperator.CONTAINS, value=["sale"]),
        JsonbFilter(field="size", op=FilterOperator.IN, value=["S", "M"]),
    ]

    clause = build_jsonb_filters(Product.attributes, filters, logic="or")
    stmt = select(Product).where(clause)
    sql = _compiled_sql(stmt, literal_binds=False)

    assert "@>" in sql or "contains" in sql.lower()
    assert "->>" in sql
    assert "IN" in sql


def test_build_jsonb_filters_exists():
    clause = build_jsonb_filters(
        Product.attributes,
        [JsonbFilter(field="brand", op=FilterOperator.EXISTS)],
    )
    stmt = select(Product).where(clause)
    sql = _compiled_sql(stmt)
    assert "brand" in sql


def test_build_jsonb_filters_invalid_logic():
    with pytest.raises(FilterError):
        build_jsonb_filters(Product.attributes, [JsonbFilter(field="x", op=FilterOperator.EQ, value="y")], logic="xor")
