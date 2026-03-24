from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

AUTH_STATUS_KEY = "is_authenticated"
TENANT_ID_KEY = "tenant_id"


def normalize_tenant_id(value: str | None) -> str:
    if not value:
        return ""
    return value.strip()


def apply_auth(session: MutableMapping[str, Any], tenant_id: str | None) -> bool:
    normalized = normalize_tenant_id(tenant_id)
    if not normalized:
        return False

    session[TENANT_ID_KEY] = normalized
    session[AUTH_STATUS_KEY] = True
    return True
