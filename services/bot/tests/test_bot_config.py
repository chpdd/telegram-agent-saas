import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

BOT_SRC = str(Path(__file__).parents[1] / "src")
API_SRC = str(Path(__file__).parents[3] / "api" / "src")
WORKER_SRC = str(Path(__file__).parents[3] / "worker" / "src")
for service_src in [BOT_SRC, API_SRC, WORKER_SRC]:
    if service_src in sys.path:
        sys.path.remove(service_src)
sys.path.insert(0, BOT_SRC)


def _reload_bot_config():
    module_name = "bot_test_config_module"
    sys.modules.pop(module_name, None)
    spec = spec_from_file_location(module_name, Path(BOT_SRC) / "core" / "config.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bot_settings_are_loaded_from_environment_and_cached(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_db")
    monkeypatch.setenv("BOT_WEBHOOK_BASE_URL", "https://example.com")
    monkeypatch.setenv("BOT_WEBHOOK_SECRET", "secret")

    config = _reload_bot_config()
    first = config.get_settings()
    second = config.get_settings()

    assert first.BOT_WEBHOOK_BASE_URL == "https://example.com"
    assert first.BOT_WEBHOOK_SECRET == "secret"
    assert first.db_url == "postgresql+asyncpg://test:test@localhost:5432/test_db"
    assert first is second
