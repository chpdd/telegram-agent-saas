from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_WEBHOOK_BASE_URL: str
    BOT_WEBHOOK_SECRET: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[4] / ".env",
        env_ignore_missing=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
