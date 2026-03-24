import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parents[1] / "src"))

from schema_designer import (  # noqa: E402
    SCHEMAS_KEY,
    add_schema,
    delete_schema,
    ensure_schema_state,
    parse_schema_payload,
    update_schema,
)


def test_parse_schema_payload_requires_json_object():
    with pytest.raises(ValueError):
        parse_schema_payload("")
    with pytest.raises(ValueError):
        parse_schema_payload("[]")

    payload = parse_schema_payload('{"field":"value"}')
    assert payload == {"field": "value"}


def test_schema_crud_flow():
    session = {}
    ensure_schema_state(session)
    assert session[SCHEMAS_KEY] == []

    entry = add_schema(session, "catalog", {"color": "red"})
    assert entry["name"] == "catalog"
    assert session[SCHEMAS_KEY][0]["payload"] == {"color": "red"}

    updated = update_schema(session, 0, "catalog-v2", {"size": "m"})
    assert updated["name"] == "catalog-v2"
    assert session[SCHEMAS_KEY][0]["payload"] == {"size": "m"}

    delete_schema(session, 0)
    assert session[SCHEMAS_KEY] == []
