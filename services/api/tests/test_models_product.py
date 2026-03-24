import os
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from models.product import Product  # noqa: E402


def test_product_model_schema():
    table = Product.__table__
    assert table.name == "products"

    id_column = table.columns["id"]
    assert isinstance(id_column.type, PG_UUID)
    assert id_column.primary_key

    tenant_id_column = table.columns["tenant_id"]
    assert isinstance(tenant_id_column.type, PG_UUID)
    assert not tenant_id_column.nullable

    name_column = table.columns["name"]
    assert not name_column.nullable

    description_column = table.columns["description"]
    assert description_column.nullable

    attributes_column = table.columns["attributes"]
    assert isinstance(attributes_column.type, JSONB)

    search_column = table.columns["search_vector"]
    assert isinstance(search_column.type, TSVECTOR)

    index_names = {index.name for index in table.indexes}
    assert "ix_products_tenant_id" in index_names
    assert "ix_products_search_vector" in index_names
