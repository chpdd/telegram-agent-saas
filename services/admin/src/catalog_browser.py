from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


def normalize_catalog_filters(
    tenant_id: str,
    category: str | None = None,
    query: str | None = None,
    limit: int = 100,
) -> dict[str, str | UUID | int | None]:
    try:
        tenant_uuid = UUID(tenant_id.strip())
    except (AttributeError, ValueError) as exc:
        raise ValueError("tenant_id должен быть валидным UUID") from exc

    normalized_limit = max(1, min(limit, 500))
    normalized_category = (category or "").strip() or None
    normalized_query = (query or "").strip() or None

    return {
        "tenant_id": tenant_uuid,
        "category": normalized_category,
        "query": normalized_query,
        "limit": normalized_limit,
    }


def list_catalog_products(
    session: Session,
    *,
    tenant_id: str,
    category: str | None = None,
    query: str | None = None,
    limit: int = 100,
) -> list[dict[str, str | float | None]]:
    filters = normalize_catalog_filters(tenant_id, category, query, limit)
    conditions = ["tenant_id = :tenant_id"]
    params: dict[str, str | UUID | int] = {
        "tenant_id": filters["tenant_id"],
        "limit": int(filters["limit"]),
    }

    if filters["category"] is not None:
        conditions.append("attributes ->> 'category' = :category")
        params["category"] = str(filters["category"])

    if filters["query"] is not None:
        conditions.append(
            """
            (
                lower(name) like lower('%' || :query || '%')
                or lower(coalesce(description, '')) like lower('%' || :query || '%')
            )
            """
        )
        params["query"] = str(filters["query"])

    result = session.execute(
        text(
            f"""
            select
                id,
                name,
                description,
                attributes ->> 'category' as category,
                attributes ->> 'measure' as measure,
                cast(attributes ->> 'price' as double precision) as price
            from products
            where {' and '.join(conditions)}
            order by category nulls last, name
            limit :limit
            """
        ),
        params,
    )
    rows = result.mappings().all()
    return [
        {
            "id": str(row["id"]),
            "name": row["name"],
            "description": row["description"],
            "category": row["category"],
            "measure": row["measure"],
            "price": row["price"],
        }
        for row in rows
    ]
