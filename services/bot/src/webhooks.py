from __future__ import annotations

from collections.abc import Iterable

from aiogram import Bot
from core.bot import build_webhook_url, create_bot
from core.config import get_settings


async def register_webhook(bot: Bot, tenant_id: str) -> None:
    settings = get_settings()
    await bot.set_webhook(
        url=build_webhook_url(tenant_id),
        secret_token=settings.BOT_WEBHOOK_SECRET,
        drop_pending_updates=True,
    )


async def register_webhooks(tokens: Iterable[tuple[str, str]]) -> None:
    for tenant_id, token in tokens:
        bot = create_bot(token)
        try:
            await register_webhook(bot, tenant_id)
        finally:
            await bot.session.close()
