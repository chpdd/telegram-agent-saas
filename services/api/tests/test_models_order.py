import os
import sys
from decimal import Decimal
from pathlib import Path

from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

os.environ.setdefault("LLM_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from models.order import Order  # noqa: E402


def test_order_model_schema():
    table = Order.__table__
    assert table.name == "orders"

    id_column = table.columns["id"]
    assert isinstance(id_column.type, PG_UUID)
    assert id_column.primary_key

    tenant_id_column = table.columns["tenant_id"]
    assert isinstance(tenant_id_column.type, PG_UUID)
    assert not tenant_id_column.nullable

    chat_id_column = table.columns["chat_id"]
    assert isinstance(chat_id_column.type, PG_UUID)
    assert not chat_id_column.nullable

    items_column = table.columns["items"]
    assert isinstance(items_column.type, JSONB)

    total_price_column = table.columns["total_price"]
    assert isinstance(total_price_column.type, Numeric)
    assert total_price_column.default.arg == Decimal("0.00")

    index_names = {index.name for index in table.indexes}
    assert "ix_orders_tenant_id" in index_names
    assert "ix_orders_chat_id" in index_names
