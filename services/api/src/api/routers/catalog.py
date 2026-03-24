from core.dependencies import get_db_session
from fastapi import APIRouter, Depends
from schemas.catalog import CatalogProductResponse, CatalogSearchRequest
from services.search import search_products
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.post("/search", response_model=list[CatalogProductResponse])
async def search_catalog(
    payload: CatalogSearchRequest,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> list[CatalogProductResponse]:
    products = await search_products(
        session,
        payload.tenant_id,
        filters=[item.to_jsonb_filter() for item in payload.filters] or None,
        logic=payload.logic,
        offset=payload.offset,
        limit=payload.limit,
    )
    return [CatalogProductResponse.model_validate(product) for product in products]
