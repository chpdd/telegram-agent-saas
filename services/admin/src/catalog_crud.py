from __future__ import annotations

import json
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def normalize_product_payload(
    tenant_id: str,
    *,
    name: str | None,
    category: str | None,
    measure: str | None,
    price: float | int | None,
    description: str | None = None,
    product_id: str | None = None,
) -> dict[str, str | UUID | float | None]:
    normalized_name = (name or "").strip()
    normalized_category = (category or "").strip()
    normalized_measure = (measure or "").strip()
    normalized_description = (description or "").strip() or None

    if not normalized_name:
        raise ValueError("Укажите название")
    if not normalized_category:
        raise ValueError("Укажите категорию")
    if not normalized_measure:
        raise ValueError("Укажите единицу измерения")
    if price is None or float(price) < 0:
        raise ValueError("Цена должна быть неотрицательной")

    try:
        tenant_uuid = UUID(tenant_id.strip())
    except (AttributeError, ValueError) as exc:
        raise ValueError("tenant_id должен быть валидным UUID") from exc

    if product_id:
        try:
            normalized_product_id = UUID(product_id.strip())
        except (AttributeError, ValueError) as exc:
            raise ValueError("product_id должен быть валидным UUID") from exc
    else:
        normalized_product_id = uuid4()

    return {
        "product_id": normalized_product_id,
        "tenant_id": tenant_uuid,
        "name": normalized_name,
        "description": normalized_description,
        "category": normalized_category,
        "measure": normalized_measure,
        "price": float(price),
    }


async def create_catalog_product(
    session: AsyncSession,
    *,
    tenant_id: str,
    name: str | None,
    category: str | None,
    measure: str | None,
    price: float | int | None,
    description: str | None = None,
) -> dict[str, str | float | None]:
    payload = normalize_product_payload(
        tenant_id,
        name=name,
        category=category,
        measure=measure,
        price=price,
        description=description,
    )
    await session.execute(
        text(
            """
            insert into products (id, tenant_id, name, description, attributes)
            values (
                :product_id,
                :tenant_id,
                :name,
                :description,
                cast(:attributes as jsonb)
            )
            """
        ),
        {
            "product_id": payload["product_id"],
            "tenant_id": payload["tenant_id"],
            "name": payload["name"],
            "description": payload["description"],
            "attributes": json.dumps(
                {
                    "category": payload["category"],
                    "measure": payload["measure"],
                    "price": payload["price"],
                    "kind": "service",
                },
                ensure_ascii=False,
            ),
        },
    )
    await session.commit()
    return {
        "id": str(payload["product_id"]),
        "name": str(payload["name"]),
        "description": payload["description"],
        "category": str(payload["category"]),
        "measure": str(payload["measure"]),
        "price": float(payload["price"]),
    }


async def update_catalog_product(
    session: AsyncSession,
    *,
    tenant_id: str,
    product_id: str,
    name: str | None,
    category: str | None,
    measure: str | None,
    price: float | int | None,
    description: str | None = None,
) -> dict[str, str | float | None]:
    payload = normalize_product_payload(
        tenant_id,
        product_id=product_id,
        name=name,
        category=category,
        measure=measure,
        price=price,
        description=description,
    )
    result = await session.execute(
        text(
            """
            update products
            set
                name = :name,
                description = :description,
                attributes = cast(:attributes as jsonb)
            where id = :product_id and tenant_id = :tenant_id
            """
        ),
        {
            "product_id": payload["product_id"],
            "tenant_id": payload["tenant_id"],
            "name": payload["name"],
            "description": payload["description"],
            "attributes": json.dumps(
                {
                    "category": payload["category"],
                    "measure": payload["measure"],
                    "price": payload["price"],
                    "kind": "service",
                },
                ensure_ascii=False,
            ),
        },
    )
    if result.rowcount != 1:
        raise ValueError("Товар не найден")
    await session.commit()
    return {
        "id": str(payload["product_id"]),
        "name": str(payload["name"]),
        "description": payload["description"],
        "category": str(payload["category"]),
        "measure": str(payload["measure"]),
        "price": float(payload["price"]),
    }


async def delete_catalog_product(
    session: AsyncSession,
    *,
    tenant_id: str,
    product_id: str,
) -> None:
    try:
        tenant_uuid = UUID(tenant_id.strip())
        product_uuid = UUID(product_id.strip())
    except (AttributeError, ValueError) as exc:
        raise ValueError("tenant_id и product_id должны быть валидными UUID") from exc

    result = await session.execute(
        text("delete from products where id = :product_id and tenant_id = :tenant_id"),
        {"product_id": product_uuid, "tenant_id": tenant_uuid},
    )
    if result.rowcount != 1:
        raise ValueError("Товар не найден")
    await session.commit()
