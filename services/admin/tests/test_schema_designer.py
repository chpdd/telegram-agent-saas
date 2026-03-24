import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1] / "src"))

from schema_designer import (  # noqa: E402
    SCHEMAS_KEY,
    add_column,
    add_schema,
    delete_column,
    delete_schema,
    ensure_schema_state,
    update_column,
    update_schema,
)


def test_schema_crud_flow():
    session = {}
    ensure_schema_state(session)
    assert session[SCHEMAS_KEY] == []

    entry = add_schema(session, "catalog")
    assert entry["name"] == "catalog"
    assert session[SCHEMAS_KEY][0]["columns"] == []

    updated = update_schema(session, 0, "catalog-v2")
    assert updated["name"] == "catalog-v2"
    assert session[SCHEMAS_KEY][0]["columns"] == []

    add_column(session, 0, "color", "Цвет", "Цвет товара")
    assert session[SCHEMAS_KEY][0]["columns"][0]["key"] == "color"

    update_column(session, 0, 0, "size", "Размер", "Размер товара")
    assert session[SCHEMAS_KEY][0]["columns"][0]["key"] == "size"

    delete_column(session, 0, 0)
    assert session[SCHEMAS_KEY][0]["columns"] == []

    delete_schema(session, 0)
    assert session[SCHEMAS_KEY] == []
