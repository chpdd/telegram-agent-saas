import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

API_SRC = str(Path(__file__).parents[1] / "src")
if API_SRC in sys.path:
    sys.path.remove(API_SRC)
sys.path.insert(0, API_SRC)

for module_name in [
    "main",
    "api",
    "api.routers",
    "api.routers.catalog",
    "api.routers.system",
    "core",
    "core.config",
    "core.dependencies",
]:
    sys.modules.pop(module_name, None)

os.environ.setdefault("LLM_API_KEY", "test")

from core.dependencies import get_db_session  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from main import create_app  # noqa: E402


async def _override_session():
    yield SimpleNamespace()


def test_health_route_works():
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_catalog_search_route_uses_session_dependency_and_returns_products(mocker):
    tenant_id = uuid4()
    product = SimpleNamespace(
        id=uuid4(),
        tenant_id=tenant_id,
        name="Red Chair",
        description="Compact chair",
        attributes={"color": "red"},
    )
    search_mock = mocker.patch("api.routers.catalog.search_products", mocker.AsyncMock(return_value=[product]))
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_session

    with TestClient(app) as client:
        response = client.post(
            "/catalog/search",
            json={
                "tenant_id": str(tenant_id),
                "filters": [{"field": "color", "op": "eq", "value": "red"}],
                "logic": "and",
                "offset": 0,
                "limit": 20,
            },
        )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(product.id),
            "tenant_id": str(product.tenant_id),
            "name": "Red Chair",
            "description": "Compact chair",
            "attributes": {"color": "red"},
        }
    ]
    search_mock.assert_awaited_once()


def test_catalog_search_route_rejects_invalid_logic():
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_session

    with TestClient(app) as client:
        response = client.post(
            "/catalog/search",
            json={
                "tenant_id": str(uuid4()),
                "filters": [],
                "logic": "xor",
            },
        )

    assert response.status_code == 422
