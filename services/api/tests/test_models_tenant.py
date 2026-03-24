import os
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import UUID as PG_UUID

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from models.tenant import Tenant  # noqa: E402


def test_tenant_model_schema():
    table = Tenant.__table__
    assert table.name == "tenants"

    id_column = table.columns["id"]
    assert isinstance(id_column.type, PG_UUID)
    assert id_column.primary_key

    bot_token_column = table.columns["bot_token"]
    assert not bot_token_column.nullable
    assert bot_token_column.unique

    system_prompt_column = table.columns["system_prompt"]
    assert system_prompt_column.nullable
