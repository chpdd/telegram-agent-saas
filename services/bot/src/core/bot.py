from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from core.config import get_settings


def create_bot(token: str) -> Bot:
    return Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))


def build_webhook_url(tenant_id: str) -> str:
    settings = get_settings()
    return f"{settings.BOT_WEBHOOK_BASE_URL.rstrip('/')}/webhooks/{tenant_id}"
