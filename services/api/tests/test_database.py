import os
import sys
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from core.database import engine, get_session  # noqa: E402


def test_engine_uses_asyncpg_driver():
    assert engine.url.drivername == "postgresql+asyncpg"


@pytest.mark.asyncio
async def test_get_session_yields_async_session():
    async for session in get_session():
        assert isinstance(session, AsyncSession)
        break
