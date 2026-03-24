import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import DateTime, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

WORKER_SRC = str(Path(__file__).parents[1] / "src")
if WORKER_SRC in sys.path:
    sys.path.remove(WORKER_SRC)
sys.path.insert(0, WORKER_SRC)

for module_name in ["inactivity"]:
    sys.modules.pop(module_name, None)

from inactivity import (  # noqa: E402
    build_close_chat_statement,
    build_inactive_chats_statement,
    close_inactive_chats,
    inactivity_cutoff,
)


class Base(DeclarativeBase):
    pass


class DummyChat(Base):
    __tablename__ = "dummy_chats"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _compiled_sql(statement):
    return str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def test_inactivity_cutoff_defaults_to_two_hours():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    cutoff = inactivity_cutoff(now=now)
    assert cutoff == now - timedelta(hours=2)


def test_build_inactive_chats_statement_filters_open_and_old():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    stmt = build_inactive_chats_statement(DummyChat, now=now)
    sql = _compiled_sql(stmt)

    assert "status = 'open'" in sql
    assert "updated_at" in sql


def test_build_close_chat_statement_sets_closed_status():
    stmt = build_close_chat_statement(DummyChat, "chat-1")
    sql = _compiled_sql(stmt)

    assert "status='closed'" in sql or "status = 'closed'" in sql


@pytest.mark.asyncio
async def test_close_inactive_chats_updates_found_rows(mocker):
    old_chat = SimpleNamespace(id=uuid4())
    session = SimpleNamespace()
    session.execute = mocker.AsyncMock(
        side_effect=[
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [old_chat])),
            None,
        ]
    )
    session.commit = mocker.AsyncMock()

    closed_ids = await close_inactive_chats(
        session,
        chat_model=DummyChat,
        now=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
    )

    assert closed_ids == [old_chat.id]
    session.commit.assert_awaited_once()
