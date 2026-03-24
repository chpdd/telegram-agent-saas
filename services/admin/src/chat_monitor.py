from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

ACTIVE_CHATS_KEY = "active_chats"


def ensure_chat_state(session: dict) -> None:
    session.setdefault(ACTIVE_CHATS_KEY, [])


def add_chat(session: dict, session_id: str, user_id: str, status: str) -> dict[str, Any]:
    ensure_chat_state(session)
    if not session_id.strip():
        raise ValueError("Session ID is required")
    if not user_id.strip():
        raise ValueError("User ID is required")
    entry = {
        "session_id": session_id.strip(),
        "user_id": user_id.strip(),
        "status": status.strip() or "open",
        "last_update": datetime.now(UTC).isoformat(),
    }
    session[ACTIVE_CHATS_KEY].append(entry)
    return entry


def remove_chat(session: dict, index: int) -> dict[str, Any]:
    ensure_chat_state(session)
    if index < 0 or index >= len(session[ACTIVE_CHATS_KEY]):
        raise IndexError("Chat not found")
    return session[ACTIVE_CHATS_KEY].pop(index)
