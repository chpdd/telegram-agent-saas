import os
import sys
from uuid import UUID, uuid4
from pathlib import Path

import pytest
from openai import RateLimitError

os.environ.setdefault("LLM_API_KEY", "test-key")

API_SRC = str(Path(__file__).parents[1] / "src")
if API_SRC in sys.path:
    sys.path.remove(API_SRC)
sys.path.insert(0, API_SRC)

from services.telegram_webhook import (  # noqa: E402
    LLM_TEMPORARY_FAILURE_MESSAGE,
    build_chat_session_id,
    extract_message_context,
    handle_telegram_webhook,
)


def test_extract_message_context_returns_text_payload():
    context = extract_message_context(
        {
            "message": {
                "text": "hello",
                "chat": {"id": 12345},
                "from": {"id": 777},
            }
        }
    )

    assert context is not None
    assert context.telegram_chat_id == "12345"
    assert context.telegram_user_id == "777"
    assert context.text == "hello"


def test_extract_message_context_ignores_unsupported_updates():
    assert extract_message_context({"callback_query": {"id": "cbq-1"}}) is None


def test_build_chat_session_id_uses_tenant_and_telegram_chat():
    assert build_chat_session_id("tenant-1", "12345") == "telegram:tenant-1:12345"


@pytest.mark.asyncio
async def test_handle_telegram_webhook_returns_fallback_on_llm_rate_limit(mocker):
    tenant = mocker.Mock(bot_token="123456:test-token", system_prompt="assistant")
    chat = mocker.Mock(id=uuid4(), session_id="telegram:tenant-1:12345")
    session = mocker.AsyncMock()
    session.rollback = mocker.AsyncMock()

    mocker.patch("services.telegram_webhook._load_tenant", new=mocker.AsyncMock(return_value=tenant))
    mocker.patch("services.telegram_webhook._get_or_create_chat", new=mocker.AsyncMock(return_value=chat))
    mocker.patch(
        "services.telegram_webhook.run_conversation_turn",
        new=mocker.AsyncMock(
            side_effect=RateLimitError(
                "rate limited",
                response=mocker.Mock(status_code=429, request=mocker.Mock()),
                body=None,
            )
        ),
    )
    bot_instance = mocker.Mock()
    bot_instance.send_message = mocker.AsyncMock()
    bot_instance.session.close = mocker.AsyncMock()
    bot_class = mocker.patch("services.telegram_webhook.Bot", return_value=bot_instance)

    result = await handle_telegram_webhook(
        session,
        tenant_id=UUID("11111111-1111-1111-1111-111111111111"),
        update={
            "message": {
                "text": "hello",
                "chat": {"id": 12345},
                "from": {"id": 777},
            }
        },
    )

    assert result["status"] == "deferred"
    assert result["reply"] == LLM_TEMPORARY_FAILURE_MESSAGE
    session.rollback.assert_awaited_once()
    bot_instance.send_message.assert_awaited_once_with(chat_id="12345", text=LLM_TEMPORARY_FAILURE_MESSAGE)
    bot_instance.session.close.assert_awaited_once()
    bot_class.assert_called_once()
