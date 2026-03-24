import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

BOT_SRC = str(Path(__file__).parents[1] / "src")
API_SRC = str(Path(__file__).parents[3] / "api" / "src")
WORKER_SRC = str(Path(__file__).parents[3] / "worker" / "src")
for service_src in [BOT_SRC, API_SRC, WORKER_SRC]:
    if service_src in sys.path:
        sys.path.remove(service_src)
sys.path.insert(0, BOT_SRC)

for module_name in ["core", "core.config", "core.bot", "webhooks", "main"]:
    sys.modules.pop(module_name, None)

from main import TenantBotConfig, build_registration_batch, load_tenant_bot_configs, run_bot_runtime  # noqa: E402


def test_build_registration_batch():
    configs = [
        TenantBotConfig(tenant_id="tenant-1", bot_token="token-1"),
        TenantBotConfig(tenant_id="tenant-2", bot_token="token-2"),
    ]

    assert build_registration_batch(configs) == [
        ("tenant-1", "token-1"),
        ("tenant-2", "token-2"),
    ]


@pytest.mark.asyncio
async def test_load_tenant_bot_configs_maps_query_rows(mocker):
    result = mocker.MagicMock()
    result.all.return_value = [("tenant-1", "token-1"), ("tenant-2", "token-2")]

    session = mocker.MagicMock()
    session.execute = mocker.AsyncMock(return_value=result)

    session_context = mocker.MagicMock()
    session_context.__aenter__ = mocker.AsyncMock(return_value=session)
    session_context.__aexit__ = mocker.AsyncMock(return_value=None)

    session_factory = mocker.MagicMock(return_value=session_context)
    fake_tenant = SimpleNamespace(id="tenant_id_column", bot_token="bot_token_column")
    mocker.patch("main.select", lambda *columns: ("select", columns))

    configs = await load_tenant_bot_configs(session_factory=session_factory, tenant_model=fake_tenant)

    assert configs == [
        TenantBotConfig(tenant_id="tenant-1", bot_token="token-1"),
        TenantBotConfig(tenant_id="tenant-2", bot_token="token-2"),
    ]
    session.execute.assert_awaited_once_with(("select", ("tenant_id_column", "bot_token_column")))


@pytest.mark.asyncio
async def test_run_bot_runtime_registers_loaded_configs(mocker):
    loader = mocker.AsyncMock(
        return_value=[TenantBotConfig(tenant_id="tenant-1", bot_token="token-1")]
    )
    registrar = mocker.AsyncMock()

    configs = await run_bot_runtime(loader=loader, registrar=registrar)

    assert configs == [TenantBotConfig(tenant_id="tenant-1", bot_token="token-1")]
    registrar.assert_awaited_once_with([("tenant-1", "token-1")])


@pytest.mark.asyncio
async def test_run_bot_runtime_skips_empty_registration_batch(mocker):
    loader = mocker.AsyncMock(return_value=[])
    registrar = mocker.AsyncMock()

    configs = await run_bot_runtime(loader=loader, registrar=registrar)

    assert configs == []
    registrar.assert_not_awaited()
