import os
import sys
from pathlib import Path

import pytest

BOT_SRC = str(Path(__file__).parents[1] / "src")
if BOT_SRC in sys.path:
    sys.path.remove(BOT_SRC)
sys.path.insert(0, BOT_SRC)

for module_name in ["core", "core.config", "core.bot"]:
    sys.modules.pop(module_name, None)

os.environ.setdefault("BOT_WEBHOOK_BASE_URL", "https://example.com")
os.environ.setdefault("BOT_WEBHOOK_SECRET", "test-secret")

from core.bot import build_webhook_url  # noqa: E402
from webhooks import register_webhook, register_webhooks  # noqa: E402


def test_build_webhook_url():
    os.environ["BOT_WEBHOOK_BASE_URL"] = "https://example.com"
    assert build_webhook_url("tenant-1") == "https://example.com/webhooks/tenant-1"


@pytest.mark.asyncio
async def test_register_webhook_calls_set_webhook(mocker):
    bot = mocker.MagicMock()
    bot.set_webhook = mocker.AsyncMock()

    await register_webhook(bot, "tenant-1")

    bot.set_webhook.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_webhooks_closes_sessions(mocker):
    mock_bot = mocker.MagicMock()
    mock_bot.set_webhook = mocker.AsyncMock()
    mock_bot.session.close = mocker.AsyncMock()

    mocker.patch("webhooks.create_bot", lambda token: mock_bot)

    await register_webhooks([("tenant-1", "token-1")])

    mock_bot.set_webhook.assert_awaited_once()
    mock_bot.session.close.assert_awaited_once()
