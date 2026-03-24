from __future__ import annotations

import json
from typing import Any

SCHEMAS_KEY = "catalog_schemas"


def ensure_schema_state(session: dict) -> None:
    session.setdefault(SCHEMAS_KEY, [])


def parse_schema_payload(raw_payload: str) -> dict[str, Any]:
    payload = raw_payload.strip()
    if not payload:
        raise ValueError("Schema payload is required")
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Schema payload must be valid JSON") from exc
    if not isinstance(data, dict):
        raise ValueError("Schema payload must be a JSON object")
    return data


def add_schema(session: dict, name: str, payload: dict[str, Any]) -> dict[str, Any]:
    ensure_schema_state(session)
    if not name.strip():
        raise ValueError("Schema name is required")
    entry = {"name": name.strip(), "payload": payload}
    session[SCHEMAS_KEY].append(entry)
    return entry


def update_schema(session: dict, index: int, name: str, payload: dict[str, Any]) -> dict[str, Any]:
    ensure_schema_state(session)
    if index < 0 or index >= len(session[SCHEMAS_KEY]):
        raise IndexError("Schema not found")
    if not name.strip():
        raise ValueError("Schema name is required")
    entry = {"name": name.strip(), "payload": payload}
    session[SCHEMAS_KEY][index] = entry
    return entry


def delete_schema(session: dict, index: int) -> None:
    ensure_schema_state(session)
    if index < 0 or index >= len(session[SCHEMAS_KEY]):
        raise IndexError("Schema not found")
    session[SCHEMAS_KEY].pop(index)
