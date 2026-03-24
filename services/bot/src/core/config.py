from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str | None = Field(default=None, validation_alias=AliasChoices("DATABASE_URL"))
    DB_NAME: str = "telegram_ai_agent"
    DB_USER: str = "user"
    DB_PASS: str = "password"
    DB_PORT: int = 5432
    DB_HOST: str = "db"

    BOT_WEBHOOK_BASE_URL: str
    BOT_WEBHOOK_SECRET: str

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[4] / ".env",
        env_ignore_missing=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
