from core.config import settings
from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "api",
        "mode": settings.MODE,
    }
