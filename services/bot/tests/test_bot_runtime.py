import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

import pytest

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
    ]:
        sys.modules.pop(module_name, None)

    config_spec = spec_from_file_location("core.config", BOT_SRC / "core" / "config.py")
    assert config_spec is not None and config_spec.loader is not None
    config_module = module_from_spec(config_spec)
    config_spec.loader.exec_module(config_module)
    sys.modules["core.config"] = config_module

    bot_spec = spec_from_file_location("core.bot", BOT_SRC / "core" / "bot.py")
    assert bot_spec is not None and bot_spec.loader is not None
    bot_core_module = module_from_spec(bot_spec)
    sys.modules["core.bot"] = bot_core_module
    bot_spec.loader.exec_module(bot_core_module)

    database_spec = spec_from_file_location("core.database", BOT_SRC / "core" / "database.py")
    assert database_spec is not None and database_spec.loader is not None
    database_module = module_from_spec(database_spec)
    sys.modules["core.database"] = database_module
    database_spec.loader.exec_module(database_module)

    tenant_spec = spec_from_file_location("models.tenant", BOT_SRC / "models" / "tenant.py")
    assert tenant_spec is not None and tenant_spec.loader is not None
    tenant_module = module_from_spec(tenant_spec)
    sys.modules["models.tenant"] = tenant_module
    tenant_spec.loader.exec_module(tenant_module)

    webhooks_spec = spec_from_file_location("webhooks", BOT_SRC / "webhooks.py")
    assert webhooks_spec is not None and webhooks_spec.loader is not None
    webhooks_module = module_from_spec(webhooks_spec)
    sys.modules["webhooks"] = webhooks_module
    webhooks_spec.loader.exec_module(webhooks_module)

    module_name = "bot_test_main"
    spec = spec_from_file_location(module_name, BOT_SRC / "main.py")
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_build_registration_batch():
    bot_main = _load_bot_main()
    configs = [
        bot_main.TenantBotConfig(tenant_id="tenant-1", bot_token="token-1"),
        bot_main.TenantBotConfig(tenant_id="tenant-2", bot_token="token-2"),
    ]

    assert bot_main.build_registration_batch(configs) == [
        ("tenant-1", "token-1"),
        ("tenant-2", "token-2"),
    ]


@pytest.mark.asyncio
async def test_load_tenant_bot_configs_maps_query_rows(mocker):
    bot_main = _load_bot_main()
    result = mocker.MagicMock()
    result.all.return_value = [("tenant-1", "token-1"), ("tenant-2", "token-2")]

    session = mocker.MagicMock()
    session.execute = mocker.AsyncMock(return_value=result)

    session_context = mocker.MagicMock()
    session_context.__aenter__ = mocker.AsyncMock(return_value=session)
    session_context.__aexit__ = mocker.AsyncMock(return_value=None)

    session_factory = mocker.MagicMock(return_value=session_context)
    fake_tenant = SimpleNamespace(id="tenant_id_column", bot_token="bot_token_column")
    mocker.patch.object(bot_main, "select", lambda *columns: ("select", columns))

    configs = await bot_main.load_tenant_bot_configs(
        session_factory=session_factory,
        tenant_model=fake_tenant,
    )

    assert configs == [
        bot_main.TenantBotConfig(tenant_id="tenant-1", bot_token="token-1"),
        bot_main.TenantBotConfig(tenant_id="tenant-2", bot_token="token-2"),
    ]
    session.execute.assert_awaited_once_with(("select", ("tenant_id_column", "bot_token_column")))


@pytest.mark.asyncio
async def test_run_bot_runtime_registers_loaded_configs(mocker):
    bot_main = _load_bot_main()
    loader = mocker.AsyncMock(
        return_value=[bot_main.TenantBotConfig(tenant_id="tenant-1", bot_token="token-1")]
    )
    registrar = mocker.AsyncMock()

    configs = await bot_main.run_bot_runtime(loader=loader, registrar=registrar)

    assert configs == [bot_main.TenantBotConfig(tenant_id="tenant-1", bot_token="token-1")]
    registrar.assert_awaited_once_with([("tenant-1", "token-1")])


@pytest.mark.asyncio
async def test_run_bot_runtime_skips_empty_registration_batch(mocker):
    bot_main = _load_bot_main()
    loader = mocker.AsyncMock(return_value=[])
    registrar = mocker.AsyncMock()

    configs = await bot_main.run_bot_runtime(loader=loader, registrar=registrar)

    assert configs == []
    registrar.assert_not_awaited()
