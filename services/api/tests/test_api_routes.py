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
    "api.routers.conversations",
    "api.routers.system",
    "api.routers.webhooks",
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


def test_conversation_route_returns_assistant_message(mocker):
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_session
    run_mock = mocker.patch(
        "api.routers.conversations.run_conversation_turn",
        mocker.AsyncMock(return_value={"content": "assistant reply", "tool_calls": []}),
    )

    with TestClient(app) as client:
        response = client.post(
            "/conversations/conv-1/messages",
            json={
                "tenant_id": str(uuid4()),
                "chat_id": str(uuid4()),
                "content": "hello",
                "model": "gpt-4o-mini",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "content": "assistant reply",
        "tool_calls": [],
    }
    run_mock.assert_awaited_once()


def test_conversation_route_returns_tool_calls(mocker):
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_session
    run_mock = mocker.patch(
        "api.routers.conversations.run_conversation_turn",
        mocker.AsyncMock(
            return_value={
                "content": "I found a chair",
                "tool_calls": [
                    {
                        "name": "catalog_tool",
                        "args": {"filters": [{"field": "color", "op": "eq", "value": "red"}]},
                        "result": [{"name": "Red Chair"}],
                    }
                ],
            }
        ),
    )

    with TestClient(app) as client:
        response = client.post(
            "/conversations/conv-2/messages",
            json={
                "tenant_id": str(uuid4()),
                "chat_id": str(uuid4()),
                "content": "find a red chair",
                "model": "gpt-4o-mini",
                "system_prompt": "You are a furniture assistant",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "content": "I found a chair",
        "tool_calls": [
            {
                "name": "catalog_tool",
                "args": {"filters": [{"field": "color", "op": "eq", "value": "red"}]},
                "result": [{"name": "Red Chair"}],
            }
        ],
    }
    run_mock.assert_awaited_once()


def test_conversation_route_rejects_empty_content():
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_session

    with TestClient(app) as client:
        response = client.post(
            "/conversations/conv-3/messages",
            json={
                "tenant_id": str(uuid4()),
                "chat_id": str(uuid4()),
                "content": "",
                "model": "gpt-4o-mini",
            },
        )

    assert response.status_code == 422


def test_webhook_route_rejects_invalid_secret():
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_session
    import api.routers.webhooks as webhook_router

    webhook_router.settings.BOT_WEBHOOK_SECRET = "test-secret"

    with TestClient(app) as client:
        response = client.post(
            f"/webhooks/{uuid4()}",
            headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
            json={"message": {"text": "hello"}},
        )

    assert response.status_code == 403


def test_webhook_route_delegates_to_handler(mocker):
    tenant_id = uuid4()
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_session
    import api.routers.webhooks as webhook_router

    webhook_router.settings.BOT_WEBHOOK_SECRET = "test-secret"
    handler_mock = mocker.patch(
        "api.routers.webhooks.handle_telegram_webhook",
        mocker.AsyncMock(
            return_value={
                "status": "processed",
                "conversation_id": "telegram:tenant:12345",
                "reply": "assistant reply",
                "tool_calls": [],
            }
        ),
    )

    with TestClient(app) as client:
        response = client.post(
            f"/webhooks/{tenant_id}",
            headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
            json={
                "message": {
                    "text": "hello",
                    "chat": {"id": 12345},
                    "from": {"id": 777},
                }
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "status": "processed",
        "conversation_id": "telegram:tenant:12345",
        "reply": "assistant reply",
        "tool_calls": [],
    }
    handler_mock.assert_awaited_once()
