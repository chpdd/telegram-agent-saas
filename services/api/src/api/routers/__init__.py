from fastapi import APIRouter

from .catalog import router as catalog_router
from .conversations import router as conversations_router
from .system import router as system_router


def build_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(system_router)
    router.include_router(catalog_router)
    router.include_router(conversations_router)
    return router
