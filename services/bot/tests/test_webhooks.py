import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

BOT_SRC = Path(__file__).parents[1] / "src"
API_SRC = Path(__file__).parents[3] / "api" / "src"
WORKER_SRC = Path(__file__).parents[3] / "worker" / "src"
for service_src in [str(BOT_SRC), str(API_SRC), str(WORKER_SRC)]:
    if service_src in sys.path:
        sys.path.remove(service_src)
sys.path.insert(0, str(BOT_SRC))

os.environ.setdefault("BOT_WEBHOOK_BASE_URL", "https://example.com")
os.environ.setdefault("BOT_WEBHOOK_SECRET", "test-secret")


def _load_bot_modules():
    for module_name in ["core", "core.config", "core.bot", "webhooks"]:
        sys.modules.pop(module_name, None)

    config_spec = spec_from_file_location("core.config", BOT_SRC / "core" / "config.py")
    assert config_spec is not None and config_spec.loader is not None
    config_module = module_from_spec(config_spec)
    sys.modules["core.config"] = config_module
    config_spec.loader.exec_module(config_module)

    bot_spec = spec_from_file_location("core.bot", BOT_SRC / "core" / "bot.py")
    assert bot_spec is not None and bot_spec.loader is not None
    bot_module = module_from_spec(bot_spec)
    sys.modules["core.bot"] = bot_module
    bot_spec.loader.exec_module(bot_module)

    webhooks_spec = spec_from_file_location("webhooks", BOT_SRC / "webhooks.py")
    assert webhooks_spec is not None and webhooks_spec.loader is not None
    webhooks_module = module_from_spec(webhooks_spec)
    sys.modules["webhooks"] = webhooks_module
    webhooks_spec.loader.exec_module(webhooks_module)

    return bot_module, webhooks_module


def test_build_webhook_url():
    bot_module, _ = _load_bot_modules()

    assert bot_module.build_webhook_url("tenant-1") == "https://example.com/webhooks/tenant-1"


@pytest.mark.asyncio
async def test_register_webhook_calls_set_webhook(mocker):
    _, webhooks_module = _load_bot_modules()
    bot = mocker.MagicMock()
    bot.set_webhook = mocker.AsyncMock()

    await webhooks_module.register_webhook(bot, "tenant-1")

    bot.set_webhook.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_webhooks_closes_sessions(mocker):
    _, webhooks_module = _load_bot_modules()
    mock_bot = mocker.MagicMock()
    mock_bot.set_webhook = mocker.AsyncMock()
    mock_bot.session.close = mocker.AsyncMock()

    mocker.patch.object(webhooks_module, "create_bot", lambda token: mock_bot)

    await webhooks_module.register_webhooks([("tenant-1", "123456:test-token")])

    mock_bot.set_webhook.assert_awaited_once()
    mock_bot.session.close.assert_awaited_once()
