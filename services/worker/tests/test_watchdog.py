import sys
from pathlib import Path

import pytest

WORKER_SRC = str(Path(__file__).parents[1] / "src")
if WORKER_SRC in sys.path:
    sys.path.remove(WORKER_SRC)
sys.path.insert(0, WORKER_SRC)

for module_name in ["core", "core.config", "watchdog"]:
    sys.modules.pop(module_name, None)

from watchdog import RedisWatchdog  # noqa: E402


class FakeRedis:
    def __init__(self) -> None:
        self.hashes: dict[str, dict[str, object]] = {}
        self.zsets: dict[str, dict[str, int]] = {}
        self.ttl: dict[str, int] = {}

    async def hset(self, key: str, mapping: dict[str, object]) -> None:
        self.hashes[key] = dict(mapping)

    async def hgetall(self, key: str) -> dict[str, object]:
        return self.hashes.get(key, {})

    async def expire(self, key: str, ttl: int) -> None:
        self.ttl[key] = ttl

    async def zadd(self, key: str, mapping: dict[str, int]) -> None:
        bucket = self.zsets.setdefault(key, {})
        bucket.update(mapping)

    async def zrangebyscore(self, key: str, min: int, max: int) -> list[str]:
        bucket = self.zsets.get(key, {})
        return [member for member, score in bucket.items() if min <= score <= max]

    async def delete(self, key: str) -> None:
        self.hashes.pop(key, None)

    async def zrem(self, key: str, member: str) -> None:
        if key in self.zsets:
            self.zsets[key].pop(member, None)


@pytest.mark.asyncio
async def test_watchdog_start_and_finish():
    redis = FakeRedis()
    watchdog = RedisWatchdog(redis, timeout_seconds=30, key_prefix="test")

    entry = await watchdog.start(conversation_id="conv-1", tenant_id="tenant-1", chat_id="chat-1")

    assert entry.conversation_id == "conv-1"
    assert redis.hashes["test:entry:conv-1"]["tenant_id"] == "tenant-1"
    assert redis.zsets["test:index"]["conv-1"] == entry.expires_at

    await watchdog.finish("conv-1")

    assert "test:entry:conv-1" not in redis.hashes
    assert "conv-1" not in redis.zsets["test:index"]


@pytest.mark.asyncio
async def test_watchdog_heartbeat_refreshes_existing_entry():
    redis = FakeRedis()
    watchdog = RedisWatchdog(redis, timeout_seconds=30, key_prefix="test")

    await watchdog.start(conversation_id="conv-1", tenant_id="tenant-1", chat_id="chat-1")
    before = redis.zsets["test:index"]["conv-1"]

    refreshed = await watchdog.heartbeat("conv-1")

    assert refreshed is not None
    assert refreshed.expires_at >= before


@pytest.mark.asyncio
async def test_watchdog_returns_expired_entries():
    redis = FakeRedis()
    watchdog = RedisWatchdog(redis, timeout_seconds=30, key_prefix="test")

    await watchdog.start(conversation_id="conv-1", tenant_id="tenant-1", chat_id="chat-1")
    await watchdog.start(conversation_id="conv-2", tenant_id="tenant-2", chat_id="chat-2")

    redis.zsets["test:index"]["conv-1"] = 10
    redis.hashes["test:entry:conv-1"]["expires_at"] = 10
    redis.zsets["test:index"]["conv-2"] = 100
    redis.hashes["test:entry:conv-2"]["expires_at"] = 100

    expired = await watchdog.expired(now=20)

    assert len(expired) == 1
    assert expired[0].conversation_id == "conv-1"
