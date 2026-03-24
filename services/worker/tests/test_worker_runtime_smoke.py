import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

WORKER_SRC = Path(__file__).parents[1] / "src"
if str(WORKER_SRC) in sys.path:
    sys.path.remove(str(WORKER_SRC))
sys.path.insert(0, str(WORKER_SRC))


def _load_worker_main():
    for module_name in [
        "core",
        "core.config",
        "core.database",
        "models",
        "models.chat",
        "inactivity",
        "session_reviewer",
        "watchdog",
        "main",
        "worker_runtime_smoke_main",
    ]:
        sys.modules.pop(module_name, None)

    for alias, relative_path in [
        ("core.config", ("core", "config.py")),
        ("core.database", ("core", "database.py")),
        ("models.chat", ("models", "chat.py")),
        ("inactivity", ("inactivity.py",)),
        ("session_reviewer", ("session_reviewer.py",)),
        ("watchdog", ("watchdog.py",)),
    ]:
        spec = spec_from_file_location(alias, WORKER_SRC.joinpath(*relative_path))
        assert spec is not None and spec.loader is not None
        module = module_from_spec(spec)
        sys.modules[alias] = module
        spec.loader.exec_module(module)

    module_name = "worker_runtime_smoke_main"
    spec = spec_from_file_location(module_name, WORKER_SRC / "main.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_worker_main_invokes_asyncio_run(mocker):
    worker_main = _load_worker_main()
    runtime = object()
    mocker.patch.object(worker_main, "build_worker_runtime", return_value=runtime)
    run_forever = mocker.patch.object(worker_main, "run_forever", mocker.AsyncMock())
    asyncio_run = mocker.patch.object(worker_main.asyncio, "run", side_effect=lambda coro: coro.close())

    worker_main.main()

    run_forever.assert_called_once_with(runtime)
    asyncio_run.assert_called_once()
