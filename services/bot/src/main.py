from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Any

from core.database import async_session_maker
from models.tenant import Tenant
from sqlalchemy import select
from webhooks import register_webhooks

logger = logging.getLogger(__name__)


LoadConfigs = Callable[[], Awaitable[list["TenantBotConfig"]]]
RegisterWebhooks = Callable[[Sequence[tuple[str, str]]], Awaitable[None]]


@dataclass(frozen=True)
class TenantBotConfig:
    tenant_id: str
    bot_token: str

async def load_tenant_bot_configs(
    *,
    session_factory: Callable[[], Any] | None = None,
    tenant_model: Any | None = None,
) -> list[TenantBotConfig]:
    if session_factory is None or tenant_model is None:
        session_factory = async_session_maker
        tenant_model = Tenant

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
