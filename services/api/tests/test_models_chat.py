import os
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import UUID as PG_UUID

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from models.chat import Chat, ChatStatus  # noqa: E402


def test_chat_model_schema():
    table = Chat.__table__
    assert table.name == "chats"

    id_column = table.columns["id"]
    assert isinstance(id_column.type, PG_UUID)
    assert id_column.primary_key

    tenant_id_column = table.columns["tenant_id"]
    assert isinstance(tenant_id_column.type, PG_UUID)
    assert not tenant_id_column.nullable

    session_id_column = table.columns["session_id"]
    assert not session_id_column.nullable
    assert session_id_column.unique

    status_column = table.columns["status"]
    assert status_column.default.arg == ChatStatus.OPEN
    assert not status_column.nullable

    user_id_column = table.columns["user_id"]
    assert not user_id_column.nullable

    index_names = {index.name for index in table.indexes}
    assert "ix_chats_tenant_id" in index_names
