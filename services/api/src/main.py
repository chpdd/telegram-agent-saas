from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from api.routers import build_api_router
from core.config import settings
from core.logging import configure_logging, get_logger
from fastapi import FastAPI

logger = get_logger(__name__)


def include_routers(app: FastAPI) -> None:
    app.include_router(build_api_router())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    app.state.settings = settings
    logger.info("API application starting", extra={"mode": settings.MODE})
    yield
    logger.info("API application stopping")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telegram Chat Agent API",
        version="0.1.0",
        lifespan=lifespan,
    )
    include_routers(app)
    return app


app = create_app()
