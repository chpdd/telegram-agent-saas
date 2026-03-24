from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session


def normalize_tenant_uuid(value: str) -> UUID:
    try:
        return UUID(value.strip())
    except (AttributeError, ValueError) as exc:
        raise ValueError("tenant_id должен быть валидным UUID") from exc


def load_seed_catalog(source_path: Path) -> list[dict]:
    raw_items = json.loads(source_path.read_text(encoding="utf-8"))
    products: list[dict] = []

    for category_entry in raw_items:
        category = str(category_entry["title"]).strip()
        for service_key, service_value in category_entry.items():
            if service_key == "title" or not isinstance(service_value, dict):
                continue

            products.append(
                {
                    "id": uuid4(),
                    "name": str(service_value["name"]).strip(),
                    "description": None,
                    "attributes": {
                        "category": category,
                        "measure": str(service_value["measure"]).strip(),
                        "price": float(service_value["price"]),
                        "kind": "service",
                    },
                }
            )

    return products


def import_seed_catalog(
    session: Session,
    *,
    tenant_id: str,
    source_path: Path,
    replace_existing: bool = True,
) -> int:
    tenant_uuid = normalize_tenant_uuid(tenant_id)
    tenant_exists = session.scalar(
        text("select 1 from tenants where id = :tenant_id"),
        {"tenant_id": tenant_uuid},
    )
    if tenant_exists != 1:
        raise ValueError("Tenant не найден")

    products = load_seed_catalog(source_path)
    if replace_existing:
        session.execute(
            text("delete from products where tenant_id = :tenant_id"),
            {"tenant_id": tenant_uuid},
        )

    rows = [
        {
            "id": product["id"],
            "tenant_id": tenant_uuid,
            "name": product["name"],
            "description": product["description"],
            "attributes": json.dumps(product["attributes"], ensure_ascii=False),
        }
        for product in products
    ]
    session.execute(
        text(
            """
            insert into products (id, tenant_id, name, description, attributes)
            values (:id, :tenant_id, :name, :description, cast(:attributes as jsonb))
            """
        ),
        rows,
    )
    session.commit()
    return len(rows)
