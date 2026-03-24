import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.dialects import postgresql

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from core.filters import FilterError, FilterOperator, JsonbFilter  # noqa: E402
from services.search import search_products  # noqa: E402


class FakeResult:
    def __init__(self, items):
        self._items = list(items)

    def scalars(self):
        return self

    def all(self):
        return list(self._items)


def _make_session(result, mocker):
    session = SimpleNamespace()
    session.execute = mocker.AsyncMock(return_value=result)
    return session


def _compiled_sql(statement):
    return str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": False},
        )
    )


@pytest.mark.asyncio
async def test_search_products_applies_tenant_and_filters(mocker):
    tenant_id = uuid4()
    session = _make_session(FakeResult([]), mocker)
    filters = [
        JsonbFilter(field="color", op=FilterOperator.EQ, value="red"),
        JsonbFilter(field="size", op=FilterOperator.IN, value=["S", "M"]),
    ]

    await search_products(session, tenant_id, filters=filters, logic="and")

    stmt = session.execute.call_args.args[0]
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql
    assert "attributes" in sql
    assert "->>" in sql
    assert "IN" in sql


@pytest.mark.asyncio
async def test_search_products_without_filters_still_scoped(mocker):
    tenant_id = uuid4()
    session = _make_session(FakeResult([]), mocker)

    await search_products(session, tenant_id, filters=None)

    stmt = session.execute.call_args.args[0]
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql


@pytest.mark.asyncio
async def test_search_products_invalid_logic_raises(mocker):
    tenant_id = uuid4()
    session = _make_session(FakeResult([]), mocker)
    filters = [JsonbFilter(field="color", op=FilterOperator.EQ, value="red")]

    with pytest.raises(FilterError):
        await search_products(session, tenant_id, filters=filters, logic="xor")


@pytest.mark.asyncio
async def test_search_products_with_or_logic_and_pagination(mocker):
    tenant_id = uuid4()
    products = [SimpleNamespace(name="Red Chair"), SimpleNamespace(name="Blue Chair")]
    session = _make_session(FakeResult(products), mocker)
    filters = [
        JsonbFilter(field="color", op=FilterOperator.EQ, value="red"),
        JsonbFilter(field="material", op=FilterOperator.EQ, value="wood"),
    ]

    results = await search_products(session, tenant_id, filters=filters, logic="or", offset=5, limit=20)

    stmt = session.execute.call_args.args[0]
    sql = _compiled_sql(stmt)
    assert " OR " in sql
    assert "OFFSET" in sql
    assert "LIMIT" in sql
    assert results == products
