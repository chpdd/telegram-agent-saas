from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

from sqlalchemy import select
from webhooks import register_webhooks

API_SRC = str(Path(__file__).parents[2] / "api" / "src")

logger = logging.getLogger(__name__)


LoadConfigs = Callable[[], Awaitable[list["TenantBotConfig"]]]
RegisterWebhooks = Callable[[Sequence[tuple[str, str]]], Awaitable[None]]


@dataclass(frozen=True)
class TenantBotConfig:
    tenant_id: str
    bot_token: str


def _import_api_module(module_name: str) -> Any:
    conflicting_modules = ["core", "core.config", "core.database", "models", "models.tenant"]
    for name in conflicting_modules:
        sys.modules.pop(name, None)
    if API_SRC in sys.path:
        sys.path.remove(API_SRC)
    sys.path.insert(0, API_SRC)
    return import_module(module_name)


async def load_tenant_bot_configs(
    *,
    session_factory: Callable[[], Any] | None = None,
    tenant_model: Any | None = None,
) -> list[TenantBotConfig]:
    if session_factory is None or tenant_model is None:
        api_database = _import_api_module("core.database")
        api_tenant = _import_api_module("models.tenant")
        session_factory = api_database.async_session_maker
        tenant_model = api_tenant.Tenant

    async with session_factory() as session:
        result = await session.execute(select(tenant_model.id, tenant_model.bot_token))

    return [TenantBotConfig(tenant_id=str(tenant_id), bot_token=bot_token) for tenant_id, bot_token in result.all()]


def build_registration_batch(configs: Sequence[TenantBotConfig]) -> list[tuple[str, str]]:
    return [(config.tenant_id, config.bot_token) for config in configs]


async def run_bot_runtime(
    *,
    loader: LoadConfigs = load_tenant_bot_configs,
    registrar: RegisterWebhooks = register_webhooks,
) -> list[TenantBotConfig]:
    configs = await loader()
    registrations = build_registration_batch(configs)
    if registrations:
        await registrar(registrations)

    logger.info("bot runtime bootstrapped", extra={"tenant_count": len(registrations)})
    return configs


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_bot_runtime())


if __name__ == "__main__":
    main()
