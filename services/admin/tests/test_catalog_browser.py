import sys
from pathlib import Path
from uuid import UUID, uuid4

import pytest

sys.path.append(str(Path(__file__).parents[1] / "src"))

from catalog_browser import list_catalog_products, normalize_catalog_filters  # noqa: E402


def test_normalize_catalog_filters_validates_and_bounds_limit():
    filters = normalize_catalog_filters(
        "11111111-1111-1111-1111-111111111111",
        category="  paint ",
        query="  red ",
        limit=1000,
    )

    assert filters == {
        "tenant_id": UUID("11111111-1111-1111-1111-111111111111"),
        "category": "paint",
        "query": "red",
        "limit": 500,
    }


def test_normalize_catalog_filters_rejects_bad_tenant():
    with pytest.raises(ValueError, match="UUID"):
        normalize_catalog_filters("bad-tenant")


def test_list_catalog_products_returns_flat_rows(mocker):
    rows = [
        {
            "id": uuid4(),
            "name": "Доставка",
            "description": None,
            "category": "Логистика",
            "measure": "рейс",
            "price": 800.0,
        }
    ]
    result = mocker.Mock()
    result.mappings.return_value.all.return_value = rows
    session = mocker.Mock()
    session.execute.return_value = result

    products = list_catalog_products(
        session,
        tenant_id="11111111-1111-1111-1111-111111111111",
        category="Логистика",
        query="Доставка",
        limit=10,
    )

    assert products == [
        {
            "id": str(rows[0]["id"]),
            "name": "Доставка",
            "description": None,
            "category": "Логистика",
            "measure": "рейс",
            "price": 800.0,
        }
    ]
    session.execute.assert_called_once()
