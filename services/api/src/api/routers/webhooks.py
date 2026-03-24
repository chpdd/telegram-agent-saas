from typing import Any
from uuid import UUID

from core.config import settings
from core.dependencies import get_db_session
from fastapi import APIRouter, Depends, Header, HTTPException, status
from services.telegram_webhook import handle_telegram_webhook
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/{tenant_id}")
async def ingest_telegram_webhook(
    tenant_id: UUID,
    payload: dict[str, Any],
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
    x_telegram_bot_api_secret_token: str | None = Header(default=None),  # noqa: B008
) -> dict[str, Any]:
    if settings.BOT_WEBHOOK_SECRET and x_telegram_bot_api_secret_token != settings.BOT_WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook secret")

    return await handle_telegram_webhook(session, tenant_id=tenant_id, update=payload)
