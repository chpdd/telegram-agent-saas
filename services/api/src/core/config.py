from pathlib import Path

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str | None = Field(default=None, validation_alias=AliasChoices("DATABASE_URL"))
    DB_NAME: str = "telegram_ai_agent"
    DB_USER: str = "user"
    DB_PASS: str = "password"
    DB_PORT: int = 5432
    DB_HOST: str = "db"

    REDIS_URL: str | None = Field(default=None, validation_alias=AliasChoices("REDIS_URL"))
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    LLM_API_KEY: str = Field(validation_alias=AliasChoices("LLM_API_KEY", "OPENROUTER_API_KEY"))
    LLM_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "OPENROUTER_BASE_URL"),
    )

    MODE: str = "DEV"

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[3] / ".env",
        env_ignore_missing=True,
        extra="ignore",
    )


settings = Settings()


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
