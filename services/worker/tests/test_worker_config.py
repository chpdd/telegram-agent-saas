import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

WORKER_SRC = str(Path(__file__).parents[1] / "src")
API_SRC = str(Path(__file__).parents[3] / "api" / "src")
BOT_SRC = str(Path(__file__).parents[3] / "bot" / "src")
for service_src in [WORKER_SRC, API_SRC, BOT_SRC]:
    if service_src in sys.path:
        sys.path.remove(service_src)
sys.path.insert(0, WORKER_SRC)


def _reload_worker_config():
    module_name = "worker_test_config_module"
    sys.modules.pop(module_name, None)
    spec = spec_from_file_location(module_name, Path(WORKER_SRC) / "core" / "config.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_worker_settings_prefer_redis_url(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/5")
    monkeypatch.setenv("REDIS_HOST", "ignored")

    config = _reload_worker_config()
    settings = config.Settings(_env_file=None)

    assert settings.redis_url == "redis://redis:6379/5"


def test_worker_settings_fall_back_to_split_redis_parts(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("REDIS_HOST", "redis")
    monkeypatch.setenv("REDIS_PORT", "6380")
    monkeypatch.setenv("LLM_API_KEY", "worker-key")

    config = _reload_worker_config()
    settings = config.Settings(_env_file=None)

    assert settings.redis_url == "redis://redis:6380/0"
    assert settings.LLM_API_KEY == "worker-key"


def test_worker_settings_accept_legacy_openrouter_aliases(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "legacy-key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://legacy.example")

    config = _reload_worker_config()
    settings = config.Settings(_env_file=None)

    assert settings.LLM_API_KEY == "legacy-key"
    assert settings.LLM_BASE_URL == "https://legacy.example"
