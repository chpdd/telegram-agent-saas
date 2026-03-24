import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

API_SRC = str(Path(__file__).parents[1] / "src")
WORKER_SRC = str(Path(__file__).parents[3] / "worker" / "src")
BOT_SRC = str(Path(__file__).parents[3] / "bot" / "src")
for service_src in [API_SRC, WORKER_SRC, BOT_SRC]:
    if service_src in sys.path:
        sys.path.remove(service_src)
sys.path.insert(0, API_SRC)


def _reload_api_config():
    module_name = "api_test_config_module"
    sys.modules.pop(module_name, None)
    spec = spec_from_file_location(module_name, Path(API_SRC) / "core" / "config.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_api_settings_prefer_database_and_redis_urls(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/runtime")
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/9")
    monkeypatch.setenv("DB_NAME", "ignored")
    monkeypatch.setenv("REDIS_HOST", "ignored")

    config = _reload_api_config()
    settings = config.Settings(_env_file=None)

    assert settings.db_url == "postgresql+asyncpg://user:pass@db:5432/runtime"
    assert settings.redis_url == "redis://redis:6379/9"


def test_api_settings_fall_back_to_split_database_parts(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("DB_NAME", "agent")
    monkeypatch.setenv("DB_USER", "user")
    monkeypatch.setenv("DB_PASS", "password")
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("REDIS_HOST", "redis")
    monkeypatch.setenv("REDIS_PORT", "6379")

    config = _reload_api_config()
    settings = config.Settings(_env_file=None)

    assert settings.db_url == "postgresql+asyncpg://user:password@db:5432/agent"
    assert settings.redis_url == "redis://redis:6379/0"
    assert config.BaseSchema.model_config["from_attributes"] is True


def test_api_settings_accept_legacy_openrouter_aliases(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "legacy-key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://legacy.example")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)

    config = _reload_api_config()
    settings = config.Settings(_env_file=None)

    assert settings.LLM_API_KEY == "legacy-key"
    assert settings.LLM_BASE_URL == "https://legacy.example"
