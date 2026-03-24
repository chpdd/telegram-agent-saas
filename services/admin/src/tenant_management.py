from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session


def prepare_tenant_payload(
    tenant_id: str | None,
    bot_token: str | None,
    system_prompt: str | None,
) -> dict[str, str | UUID | None]:
    normalized_bot_token = (bot_token or "").strip()
    if not normalized_bot_token:
        raise ValueError("Укажите bot token")

    normalized_tenant_id = (tenant_id or "").strip()
    if normalized_tenant_id:
        try:
            tenant_uuid = UUID(normalized_tenant_id)
        except ValueError as exc:
            raise ValueError("tenant_id должен быть валидным UUID") from exc
    else:
        tenant_uuid = uuid4()

    normalized_prompt = (system_prompt or "").strip() or None
    return {
        "tenant_id": tenant_uuid,
        "bot_token": normalized_bot_token,
        "system_prompt": normalized_prompt,
    }


def mask_bot_token(bot_token: str) -> str:
    if len(bot_token) <= 8:
        return "*" * len(bot_token)
    return f"{bot_token[:4]}...{bot_token[-4:]}"


def create_tenant(
    session: Session,
    *,
    tenant_id: str | None,
    bot_token: str | None,
    system_prompt: str | None,
) -> dict[str, str | None]:
    payload = prepare_tenant_payload(tenant_id, bot_token, system_prompt)
    session.execute(
        text(
            """
            insert into tenants (id, bot_token, system_prompt)
            values (:tenant_id, :bot_token, :system_prompt)
            """
        ),
        payload,
    )
    session.commit()
    return {
        "tenant_id": str(payload["tenant_id"]),
        "bot_token": str(payload["bot_token"]),
        "system_prompt": payload["system_prompt"],
    }


def list_tenants(session: Session) -> list[dict[str, str | None]]:
    result = session.execute(
        text(
            """
            select id, bot_token, system_prompt
            from tenants
            order by id
            """
        )
    )
    rows = result.mappings().all()
    return [
        {
            "tenant_id": str(row["id"]),
            "bot_token": mask_bot_token(str(row["bot_token"])),
            "system_prompt": row["system_prompt"],
        }
        for row in rows
    ]
