from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Any

from core.config import settings
from redis.asyncio import Redis


@dataclass(frozen=True)
class WatchdogEntry:
    conversation_id: str
    tenant_id: str
    chat_id: str
    expires_at: int


class RedisWatchdog:
    def __init__(
        self,
        redis: Redis,
        *,
        timeout_seconds: int | None = None,
        key_prefix: str | None = None,
    ) -> None:
        self.redis = redis
        self.timeout_seconds = timeout_seconds or settings.WATCHDOG_TIMEOUT_SECONDS
        self.key_prefix = key_prefix or settings.WATCHDOG_KEY_PREFIX

    def _entry_key(self, conversation_id: str) -> str:
        return f"{self.key_prefix}:entry:{conversation_id}"

    def _index_key(self) -> str:
        return f"{self.key_prefix}:index"

    async def start(self, *, conversation_id: str, tenant_id: str, chat_id: str) -> WatchdogEntry:
        expires_at = int(time()) + self.timeout_seconds
        entry = WatchdogEntry(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            chat_id=chat_id,
            expires_at=expires_at,
        )
        await self.redis.hset(
            self._entry_key(conversation_id),
            mapping={
                "conversation_id": conversation_id,
                "tenant_id": tenant_id,
                "chat_id": chat_id,
                "expires_at": expires_at,
            },
        )
        await self.redis.expire(self._entry_key(conversation_id), self.timeout_seconds)
        await self.redis.zadd(self._index_key(), {conversation_id: expires_at})
        return entry

    async def heartbeat(self, conversation_id: str) -> WatchdogEntry | None:
        payload = await self.redis.hgetall(self._entry_key(conversation_id))
        if not payload:
            return None

        tenant_id = _decode(payload["tenant_id"])
        chat_id = _decode(payload["chat_id"])
        return await self.start(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            chat_id=chat_id,
        )

    async def finish(self, conversation_id: str) -> None:
        await self.redis.delete(self._entry_key(conversation_id))
        await self.redis.zrem(self._index_key(), conversation_id)

    async def expired(self, *, now: int | None = None) -> list[WatchdogEntry]:
        current_time = now or int(time())
        conversation_ids = await self.redis.zrangebyscore(self._index_key(), min=0, max=current_time)
        entries: list[WatchdogEntry] = []
        for raw_conversation_id in conversation_ids:
            conversation_id = _decode(raw_conversation_id)
            payload = await self.redis.hgetall(self._entry_key(conversation_id))
            if not payload:
                await self.redis.zrem(self._index_key(), conversation_id)
                continue
            entries.append(
                WatchdogEntry(
                    conversation_id=conversation_id,
                    tenant_id=_decode(payload["tenant_id"]),
                    chat_id=_decode(payload["chat_id"]),
                    expires_at=int(_decode(payload["expires_at"])),
                )
            )
        return entries


def _decode(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode()
    return str(value)
