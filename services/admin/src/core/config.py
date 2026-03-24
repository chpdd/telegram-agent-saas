from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/telegram_ai_agent"
    REDIS_URL: str = "redis://redis:6379/0"
    MODE: str = "DEV"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[4] / ".env",
        env_ignore_missing=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
