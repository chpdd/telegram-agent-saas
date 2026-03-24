from __future__ import annotations

from typing import Any

SCHEMAS_KEY = "catalog_schemas"


def ensure_schema_state(session: dict) -> None:
    session.setdefault(SCHEMAS_KEY, [])


def _normalize(value: str) -> str:
    return value.strip()


def add_schema(session: dict, name: str) -> dict[str, Any]:
    ensure_schema_state(session)
    if not name.strip():
        raise ValueError("Schema name is required")
    entry = {"name": name.strip(), "columns": []}
    session[SCHEMAS_KEY].append(entry)
    return entry


def update_schema(session: dict, index: int, name: str) -> dict[str, Any]:
    ensure_schema_state(session)
    if index < 0 or index >= len(session[SCHEMAS_KEY]):
        raise IndexError("Schema not found")
    if not name.strip():
        raise ValueError("Schema name is required")
    session[SCHEMAS_KEY][index]["name"] = name.strip()
    return session[SCHEMAS_KEY][index]


def delete_schema(session: dict, index: int) -> None:
    ensure_schema_state(session)
    if index < 0 or index >= len(session[SCHEMAS_KEY]):
        raise IndexError("Schema not found")
    session[SCHEMAS_KEY].pop(index)


def _build_column(key: str, label: str, description: str) -> dict[str, str]:
    if not _normalize(key):
        raise ValueError("Column key is required")
    if not _normalize(label):
        raise ValueError("Column label is required")
    return {"key": _normalize(key), "label": _normalize(label), "description": description.strip()}


def add_column(session: dict, schema_index: int, key: str, label: str, description: str) -> dict[str, str]:
    ensure_schema_state(session)
    if schema_index < 0 or schema_index >= len(session[SCHEMAS_KEY]):
        raise IndexError("Schema not found")
    column = _build_column(key, label, description)
    session[SCHEMAS_KEY][schema_index]["columns"].append(column)
    return column


def update_column(
    session: dict,
    schema_index: int,
    column_index: int,
    key: str,
    label: str,
    description: str,
) -> dict[str, str]:
    ensure_schema_state(session)
    if schema_index < 0 or schema_index >= len(session[SCHEMAS_KEY]):
        raise IndexError("Schema not found")
    columns = session[SCHEMAS_KEY][schema_index]["columns"]
    if column_index < 0 or column_index >= len(columns):
        raise IndexError("Column not found")
    column = _build_column(key, label, description)
    columns[column_index] = column
    return column


def delete_column(session: dict, schema_index: int, column_index: int) -> None:
    ensure_schema_state(session)
    if schema_index < 0 or schema_index >= len(session[SCHEMAS_KEY]):
        raise IndexError("Schema not found")
    columns = session[SCHEMAS_KEY][schema_index]["columns"]
    if column_index < 0 or column_index >= len(columns):
        raise IndexError("Column not found")
    columns.pop(column_index)
