import json
import sys
from pathlib import Path
from uuid import UUID

import pytest

sys.path.append(str(Path(__file__).parents[1] / "src"))

from catalog_seed import import_seed_catalog, load_seed_catalog, normalize_tenant_uuid  # noqa: E402


def test_normalize_tenant_uuid_validates_input():
    parsed = normalize_tenant_uuid("11111111-1111-1111-1111-111111111111")

    assert parsed == UUID("11111111-1111-1111-1111-111111111111")

    with pytest.raises(ValueError, match="UUID"):
        normalize_tenant_uuid("not-a-uuid")


def test_load_seed_catalog_extracts_products(tmp_path: Path):
    source = tmp_path / "services.json"
    source.write_text(
        json.dumps(
            [
                {
                    "title": "Логистика",
                    "s1": {"name": "Доставка", "measure": "рейс", "price": 800},
                    "s2": {"name": "Грузчики", "measure": "час", "price": 900},
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    products = load_seed_catalog(source)

    assert len(products) == 2
    assert products[0]["name"] == "Доставка"
    assert products[0]["attributes"] == {
        "category": "Логистика",
        "measure": "рейс",
        "price": 800.0,
        "kind": "service",
    }


def test_import_seed_catalog_replaces_existing_rows(mocker, tmp_path: Path):
    source = tmp_path / "services.json"
    source.write_text(
        json.dumps(
            [{"title": "Категория", "s1": {"name": "Услуга", "measure": "шт.", "price": 10}}],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    session = mocker.Mock()
    session.scalar.return_value = 1

    count = import_seed_catalog(
        session,
        tenant_id="11111111-1111-1111-1111-111111111111",
        source_path=source,
    )

    assert count == 1
    session.scalar.assert_called_once()
    assert session.execute.call_count == 2
    session.commit.assert_called_once()


def test_import_seed_catalog_requires_existing_tenant(mocker, tmp_path: Path):
    source = tmp_path / "services.json"
    source.write_text("[]", encoding="utf-8")
    session = mocker.Mock()
    session.scalar.return_value = None

    with pytest.raises(ValueError, match="Tenant не найден"):
        import_seed_catalog(
            session,
            tenant_id="11111111-1111-1111-1111-111111111111",
            source_path=source,
        )
