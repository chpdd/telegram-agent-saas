import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

BOT_SRC = Path(__file__).parents[1] / "src"
API_SRC = Path(__file__).parents[3] / "api" / "src"
WORKER_SRC = Path(__file__).parents[3] / "worker" / "src"
for service_src in [str(BOT_SRC), str(API_SRC), str(WORKER_SRC)]:
    if service_src in sys.path:
        sys.path.remove(service_src)
sys.path.insert(0, str(BOT_SRC))


def _load_bot_main():
    for module_name in [
        "core",
        "core.config",
        "core.database",
        "core.bot",
        "models",
        "models.tenant",
        "webhooks",
        "main",
        "bot_runtime_smoke_main",
    ]:
        sys.modules.pop(module_name, None)

    for alias, relative_path in [
        ("core.config", ("core", "config.py")),
        ("core.bot", ("core", "bot.py")),
        ("core.database", ("core", "database.py")),
        ("models.tenant", ("models", "tenant.py")),
        ("webhooks", ("webhooks.py",)),
    ]:
        spec = spec_from_file_location(alias, BOT_SRC.joinpath(*relative_path))
        assert spec is not None and spec.loader is not None
        module = module_from_spec(spec)
        sys.modules[alias] = module
        spec.loader.exec_module(module)

    module_name = "bot_runtime_smoke_main"
    spec = spec_from_file_location(module_name, BOT_SRC / "main.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_bot_main_invokes_asyncio_run(mocker):
    bot_main = _load_bot_main()
    run_runtime = mocker.patch.object(bot_main, "run_bot_runtime", mocker.AsyncMock())
    asyncio_run = mocker.patch.object(bot_main.asyncio, "run", side_effect=lambda coro: coro.close())

    bot_main.main()

    run_runtime.assert_called_once()
    asyncio_run.assert_called_once()
