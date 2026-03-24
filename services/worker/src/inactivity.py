from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Select, Update, select, update
from sqlalchemy.ext.asyncio import AsyncSession


def inactivity_cutoff(*, now: datetime | None = None, timeout_seconds: int = 7200) -> datetime:
    reference = now or datetime.now(UTC)
    return reference - timedelta(seconds=timeout_seconds)


def build_inactive_chats_statement(
    chat_model: type[Any],
    *,
    now: datetime | None = None,
    timeout_seconds: int = 7200,
) -> Select[Any]:
    cutoff = inactivity_cutoff(now=now, timeout_seconds=timeout_seconds)
    return select(chat_model).where(
        chat_model.status == "open",
        chat_model.updated_at <= cutoff,
    )


def build_close_chat_statement(chat_model: type[Any], chat_id: object) -> Update:
    return (
        update(chat_model)
        .where(chat_model.id == chat_id)
        .values(status="closed")
    )


async def close_inactive_chats(
    session: AsyncSession,
    *,
    chat_model: type[Any],
    now: datetime | None = None,
    timeout_seconds: int = 7200,
) -> list[object]:
    statement = build_inactive_chats_statement(
        chat_model,
        now=now,
        timeout_seconds=timeout_seconds,
    )
    result = await session.execute(statement)
    chats = list(result.scalars().all())

    closed_ids: list[object] = []
    for chat in chats:
        await session.execute(build_close_chat_statement(chat_model, chat.id))
        closed_ids.append(chat.id)

    if closed_ids:
        await session.commit()

    return closed_ids
