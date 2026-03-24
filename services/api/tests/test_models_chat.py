import os
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import UUID as PG_UUID

os.environ.setdefault("OPENROUTER_API_KEY", "test")
API_SRC = str(Path(__file__).parents[1] / "src")
if API_SRC in sys.path:
    sys.path.remove(API_SRC)
sys.path.insert(0, API_SRC)

for module_name in ["core", "core.config", "core.database", "models", "models.chat"]:
    sys.modules.pop(module_name, None)

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

    updated_at_column = table.columns["updated_at"]
    assert not updated_at_column.nullable
    assert updated_at_column.server_default is not None

    index_names = {index.name for index in table.indexes}
    assert "ix_chats_tenant_id" in index_names
