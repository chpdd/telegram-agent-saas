from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from core.config import settings
from core.database import async_session_maker
from inactivity import close_inactive_chats
from models.chat import Chat
from redis.asyncio import Redis
from session_reviewer import review_session
from watchdog import RedisWatchdog

logger = logging.getLogger(__name__)


ReviewCallback = Callable[[list[dict[str, Any]]], Awaitable[list[Any]]]


@dataclass
class WorkerRuntime:
    watchdog: RedisWatchdog
    session_factory: Callable[[], Any]
    chat_model: type[Any]
    inactivity_timeout_seconds: int
    review_enabled: bool
    review_callback: ReviewCallback | None = None


async def default_review_callback(expired_entries: list[dict[str, Any]]) -> list[Any]:
    if not settings.SESSION_REVIEW_ENABLED:
        return []

    results: list[Any] = []
    for entry in expired_entries:
        transcript = entry.get("messages") or []
        if not transcript:
            continue

        result = await review_session(
            transcript,
            model=entry["model"],
            system_prompt=entry.get("system_prompt"),
        )
        results.append(result)
    return results

def build_worker_runtime() -> WorkerRuntime:
    redis = Redis.from_url(settings.redis_url)
    watchdog = RedisWatchdog(
        redis,
        timeout_seconds=settings.WATCHDOG_TIMEOUT_SECONDS,
        key_prefix=settings.WATCHDOG_KEY_PREFIX,
    )
    return WorkerRuntime(
        watchdog=watchdog,
        session_factory=async_session_maker,
        chat_model=Chat,
        inactivity_timeout_seconds=settings.INACTIVITY_TIMEOUT_SECONDS,
        review_enabled=settings.SESSION_REVIEW_ENABLED,
        review_callback=None,
    )


async def process_watchdog(runtime: WorkerRuntime) -> list[dict[str, Any]]:
    expired_entries = await runtime.watchdog.expired()
    normalized = [
        {
            "conversation_id": entry.conversation_id,
            "tenant_id": entry.tenant_id,
            "chat_id": entry.chat_id,
            "expires_at": entry.expires_at,
        }
        for entry in expired_entries
    ]
    for entry in expired_entries:
        await runtime.watchdog.finish(entry.conversation_id)
    return normalized


async def process_inactivity(runtime: WorkerRuntime) -> list[Any]:
    async with runtime.session_factory() as session:
        return await close_inactive_chats(
            session,
            chat_model=runtime.chat_model,
            timeout_seconds=runtime.inactivity_timeout_seconds,
        )


async def process_reviews(runtime: WorkerRuntime, expired_entries: list[dict[str, Any]]) -> list[Any]:
    if not runtime.review_enabled or runtime.review_callback is None:
        return []
    return await runtime.review_callback(expired_entries)


async def run_once(runtime: WorkerRuntime) -> dict[str, Any]:
    expired_entries = await process_watchdog(runtime)
    closed_chat_ids = await process_inactivity(runtime)
    reviews = await process_reviews(runtime, expired_entries)
    return {
        "expired_entries": expired_entries,
        "closed_chat_ids": closed_chat_ids,
        "reviews": reviews,
    }


async def run_forever(
    runtime: WorkerRuntime,
    *,
    poll_interval_seconds: float | None = None,
) -> None:
    interval = settings.WORKER_POLL_INTERVAL_SECONDS if poll_interval_seconds is None else poll_interval_seconds
    while True:
        result = await run_once(runtime)
        logger.info(
            "worker iteration completed",
            extra={
                "expired_count": len(result["expired_entries"]),
                "closed_count": len(result["closed_chat_ids"]),
                "review_count": len(result["reviews"]),
            },
        )
        await asyncio.sleep(interval)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_forever(build_worker_runtime()))


if __name__ == "__main__":
    main()
