from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from aiogram import Bot
from core.config import settings
from fastapi import HTTPException, status
from models.chat import Chat, ChatStatus
from models.tenant import Tenant
from services.conversation import run_conversation_turn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class TelegramMessageContext:
    telegram_chat_id: str
    telegram_user_id: str
    text: str


def extract_message_context(update: dict[str, Any]) -> TelegramMessageContext | None:
    message = update.get("message")
    if not isinstance(message, dict):
        return None

    text = message.get("text")
    chat = message.get("chat")
    sender = message.get("from")
    if not text or not isinstance(chat, dict) or not isinstance(sender, dict):
        return None

    chat_id = chat.get("id")
    user_id = sender.get("id")
    if chat_id is None or user_id is None:
        return None

    return TelegramMessageContext(
        telegram_chat_id=str(chat_id),
        telegram_user_id=str(user_id),
        text=text,
    )


def build_chat_session_id(tenant_id: UUID | str, telegram_chat_id: str) -> str:
    return f"telegram:{tenant_id}:{telegram_chat_id}"


async def _load_tenant(session: AsyncSession, tenant_id: UUID) -> Tenant:
    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant


async def _get_or_create_chat(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    telegram_chat_id: str,
    telegram_user_id: str,
) -> Chat:
    session_id = build_chat_session_id(tenant_id, telegram_chat_id)
    result = await session.execute(
        select(Chat).where(Chat.tenant_id == tenant_id, Chat.session_id == session_id)
    )
    chat = result.scalar_one_or_none()
    if chat is not None:
        chat.updated_at = datetime.now(UTC).replace(tzinfo=None)
        await session.commit()
        return chat

    chat = Chat(
        tenant_id=tenant_id,
        session_id=session_id,
        user_id=telegram_user_id,
        status=ChatStatus.OPEN,
    )
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat


async def handle_telegram_webhook(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    update: dict[str, Any],
) -> dict[str, Any]:
    context = extract_message_context(update)
    if context is None:
        return {"status": "ignored", "reason": "unsupported_update"}

    tenant = await _load_tenant(session, tenant_id)
    chat = await _get_or_create_chat(
        session,
        tenant_id=tenant_id,
        telegram_chat_id=context.telegram_chat_id,
        telegram_user_id=context.telegram_user_id,
    )

    result = await run_conversation_turn(
        session,
        tenant_id=tenant_id,
        chat_id=chat.id,
        conversation_id=chat.session_id,
        user_content=context.text,
        model=settings.DEFAULT_LLM_MODEL,
        system_prompt=tenant.system_prompt,
    )

    bot = Bot(token=tenant.bot_token, parse_mode="HTML")
    try:
        await bot.send_message(chat_id=context.telegram_chat_id, text=result["content"])
    finally:
        await bot.session.close()

    return {
        "status": "processed",
        "conversation_id": chat.session_id,
        "reply": result["content"],
        "tool_calls": result["tool_calls"],
    }
