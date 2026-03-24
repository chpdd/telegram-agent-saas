import os
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import UUID as PG_UUID

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from models.message import Message, MessageRole  # noqa: E402


def test_message_model_schema():
    table = Message.__table__
    assert table.name == "messages"

    id_column = table.columns["id"]
    assert isinstance(id_column.type, PG_UUID)
    assert id_column.primary_key

    tenant_id_column = table.columns["tenant_id"]
    assert isinstance(tenant_id_column.type, PG_UUID)
    assert not tenant_id_column.nullable

    chat_id_column = table.columns["chat_id"]
    assert isinstance(chat_id_column.type, PG_UUID)
    assert not chat_id_column.nullable

    role_column = table.columns["role"]
    assert role_column.default is None
    assert not role_column.nullable
    assert set(MessageRole) == {MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM}

    content_column = table.columns["content"]
    assert not content_column.nullable

    latency_column = table.columns["latency_ms"]
    assert latency_column.nullable

    index_names = {index.name for index in table.indexes}
    assert "ix_messages_tenant_id" in index_names
    assert "ix_messages_chat_id" in index_names
