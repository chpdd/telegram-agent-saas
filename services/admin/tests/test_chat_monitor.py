import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parents[1] / "src"))

from chat_monitor import ACTIVE_CHATS_KEY, add_chat, ensure_chat_state, remove_chat  # noqa: E402


def test_chat_monitor_add_remove_flow():
    session = {}
    ensure_chat_state(session)
    assert session[ACTIVE_CHATS_KEY] == []

    entry = add_chat(session, "sess-1", "user-1", "open")
    assert entry["session_id"] == "sess-1"
    assert entry["user_id"] == "user-1"
    assert entry["status"] == "open"
    assert len(session[ACTIVE_CHATS_KEY]) == 1

    removed = remove_chat(session, 0)
    assert removed["session_id"] == "sess-1"
    assert session[ACTIVE_CHATS_KEY] == []


def test_chat_monitor_validates_inputs():
    session = {}
    with pytest.raises(ValueError):
        add_chat(session, "", "user-1", "open")
    with pytest.raises(ValueError):
        add_chat(session, "sess-1", "", "open")

    with pytest.raises(IndexError):
        remove_chat(session, 0)
