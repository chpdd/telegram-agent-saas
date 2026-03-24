import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

os.environ.setdefault("LLM_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from core.filters import FilterOperator  # noqa: E402
from services.catalog_tool import (  # noqa: E402
    CatalogFilterInput,
    build_catalog_tool,
    run_catalog_tool,
    serialize_product,
)


class FakeProduct:
    def __init__(self):
        self.id = uuid4()
        self.tenant_id = uuid4()
        self.name = "Sneakers"
        self.description = "Running shoes"
        self.attributes = {"color": "red", "size": "42"}


@pytest.mark.asyncio
async def test_run_catalog_tool_serializes_products(mocker):
    product = FakeProduct()
    mocker.patch(
        "services.catalog_tool.search_products",
        new=mocker.AsyncMock(return_value=[product]),
    )

    result = await run_catalog_tool(
        session=SimpleNamespace(),
        tenant_id=str(product.tenant_id),
        filters=[CatalogFilterInput(field="color", op=FilterOperator.EQ, value="red")],
        limit=10,
    )

    assert result == [serialize_product(product)]


@pytest.mark.asyncio
async def test_build_catalog_tool_invokes_search(mocker):
    product = FakeProduct()
    mocker.patch(
        "services.catalog_tool.search_products",
        new=mocker.AsyncMock(return_value=[product]),
    )

    tool = build_catalog_tool(SimpleNamespace(), str(product.tenant_id))
    result = await tool.ainvoke(
        {
            "filters": [{"field": "color", "op": "eq", "value": "red"}],
            "logic": "and",
            "offset": 0,
            "limit": 5,
        }
    )

    assert result == [serialize_product(product)]


def test_serialize_product_returns_plain_dict():
    product = FakeProduct()
    payload = serialize_product(product)

    assert payload["name"] == "Sneakers"
    assert payload["attributes"] == {"color": "red", "size": "42"}
    assert payload["id"] == str(product.id)
