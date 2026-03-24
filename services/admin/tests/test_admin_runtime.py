import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ADMIN_SRC = Path(__file__).parents[1] / "src"
if str(ADMIN_SRC) in sys.path:
    sys.path.remove(str(ADMIN_SRC))
sys.path.insert(0, str(ADMIN_SRC))


def _load_admin_main():
    for module_name in ["core", "core.config", "main"]:
        sys.modules.pop(module_name, None)

    core_spec = spec_from_file_location("core.config", ADMIN_SRC / "core" / "config.py")
    assert core_spec is not None and core_spec.loader is not None
    core_module = module_from_spec(core_spec)
    core_spec.loader.exec_module(core_module)
    sys.modules["core.config"] = core_module

    spec = spec_from_file_location("admin_test_main", ADMIN_SRC / "main.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_admin_config():
    for module_name in ["core", "core.config"]:
        sys.modules.pop(module_name, None)

    spec = spec_from_file_location("admin_test_config", ADMIN_SRC / "core" / "config.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules["core.config"] = module
    return module


def test_admin_settings_are_loaded_from_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://runtime")
    monkeypatch.setenv("REDIS_URL", "redis://runtime")
    monkeypatch.setenv("MODE", "TEST")

    config = _load_admin_config()
    settings = config.Settings(_env_file=None)

    assert settings.DATABASE_URL == "postgresql+asyncpg://runtime"
    assert settings.REDIS_URL == "redis://runtime"
    assert settings.MODE == "TEST"


def test_bootstrap_runtime_sets_page_config_and_session_state(mocker):
    admin_main = _load_admin_main()
    mocker.patch.object(admin_main, "get_settings", return_value=admin_main.Settings(MODE="TEST"))
    page_config_mock = mocker.patch.object(admin_main.st, "set_page_config")
    admin_main.st.session_state.clear()

    settings = admin_main.bootstrap_runtime()

    assert admin_main.st.session_state[admin_main.RUNTIME_SETTINGS_KEY] == settings
    page_config_mock.assert_called_once_with(
        page_title="Telegram Chat Agent Admin",
        layout="wide",
    )


def test_run_async_reuses_single_event_loop():
    admin_main = _load_admin_main()

    first_result = admin_main.run_async(_noop("first"))
    second_result = admin_main.run_async(_noop("second"))

    assert first_result == "first"
    assert second_result == "second"
    assert admin_main.get_admin_event_loop() is admin_main.get_admin_event_loop()


async def _noop(value: str):
    return value
