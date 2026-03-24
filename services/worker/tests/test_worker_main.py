import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

import pytest

WORKER_SRC = str(Path(__file__).parents[1] / "src")
if WORKER_SRC in sys.path:
    sys.path.remove(WORKER_SRC)
sys.path.insert(0, WORKER_SRC)


def _load_worker_main():
    module_name = "worker_test_main_module"
    sys.modules.pop(module_name, None)
    spec = spec_from_file_location(module_name, Path(WORKER_SRC) / "main.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class FakeWatchdog:
    def __init__(self, entries):
        self.entries = list(entries)
        self.finished: list[str] = []

    async def expired(self):
        return list(self.entries)

    async def finish(self, conversation_id: str):
        self.finished.append(conversation_id)


class FakeSessionContext:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        return False


def test_build_worker_runtime_uses_configured_dependencies(mocker):
    worker_main = _load_worker_main()
    redis_instance = object()
    watchdog_instance = object()
    session_factory = object()
    chat_model = object()
    mocker.patch.object(worker_main.settings, "REDIS_URL", "redis://redis:6379/0")
    mocker.patch.object(worker_main.settings, "WATCHDOG_TIMEOUT_SECONDS", 45)
    mocker.patch.object(worker_main.settings, "WATCHDOG_KEY_PREFIX", "runtime")
    mocker.patch.object(worker_main.settings, "INACTIVITY_TIMEOUT_SECONDS", 900)
    mocker.patch.object(worker_main.settings, "SESSION_REVIEW_ENABLED", False)
    mocker.patch("redis.asyncio.Redis.from_url", return_value=redis_instance)
    mocker.patch.object(worker_main, "RedisWatchdog", return_value=watchdog_instance)
    mocker.patch.object(
        worker_main,
        "_import_api_module",
        side_effect=[
            SimpleNamespace(async_session_maker=session_factory),
            SimpleNamespace(Chat=chat_model),
        ],
    )

    runtime = worker_main.build_worker_runtime()

    assert runtime.watchdog is watchdog_instance
    assert runtime.session_factory is session_factory
    assert runtime.chat_model is chat_model
    assert runtime.inactivity_timeout_seconds == 900
    assert runtime.review_enabled is False


@pytest.mark.asyncio
async def test_run_once_processes_watchdog_inactivity_and_reviews(mocker):
    worker_main = _load_worker_main()
    expired_entry = SimpleNamespace(
        conversation_id="conv-1",
        tenant_id="tenant-1",
        chat_id="chat-1",
        expires_at=10,
    )
    watchdog = FakeWatchdog([expired_entry])
    session = object()
    review_callback = mocker.AsyncMock(return_value=[{"summary": "done"}])
    runtime = worker_main.WorkerRuntime(
        watchdog=watchdog,
        session_factory=lambda: FakeSessionContext(session),
        chat_model=object(),
        inactivity_timeout_seconds=600,
        review_enabled=True,
        review_callback=review_callback,
    )
    close_mock = mocker.patch.object(worker_main, "close_inactive_chats", mocker.AsyncMock(return_value=["chat-1"]))

    result = await worker_main.run_once(runtime)

    assert result == {
        "expired_entries": [
            {
                "conversation_id": "conv-1",
                "tenant_id": "tenant-1",
                "chat_id": "chat-1",
                "expires_at": 10,
            }
        ],
        "closed_chat_ids": ["chat-1"],
        "reviews": [{"summary": "done"}],
    }
    assert watchdog.finished == ["conv-1"]
    close_mock.assert_awaited_once_with(
        session,
        chat_model=runtime.chat_model,
        timeout_seconds=600,
    )
    review_callback.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_forever_uses_poll_interval(mocker):
    worker_main = _load_worker_main()
    runtime = worker_main.WorkerRuntime(
        watchdog=FakeWatchdog([]),
        session_factory=lambda: FakeSessionContext(object()),
        chat_model=object(),
        inactivity_timeout_seconds=600,
        review_enabled=False,
        review_callback=None,
    )
    mocker.patch.object(
        worker_main,
        "run_once",
        mocker.AsyncMock(return_value={"expired_entries": [], "closed_chat_ids": [], "reviews": []}),
    )

    class StopLoop(Exception):
        pass

    async def stop_after_first_sleep(interval):
        raise StopLoop(interval)

    mocker.patch.object(worker_main.asyncio, "sleep", stop_after_first_sleep)

    with pytest.raises(StopLoop) as exc_info:
        await worker_main.run_forever(runtime, poll_interval_seconds=0.25)

    assert exc_info.value.args == (0.25,)
