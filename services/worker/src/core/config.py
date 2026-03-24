from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str | None = Field(default=None, validation_alias=AliasChoices("DATABASE_URL"))
    REDIS_URL: str | None = Field(default=None, validation_alias=AliasChoices("REDIS_URL"))
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    LLM_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LLM_API_KEY", "OPENROUTER_API_KEY"),
    )
    LLM_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "OPENROUTER_BASE_URL"),
    )
    WATCHDOG_TIMEOUT_SECONDS: int = 30
    WATCHDOG_KEY_PREFIX: str = "watchdog"
    WORKER_POLL_INTERVAL_SECONDS: float = 5.0
    INACTIVITY_TIMEOUT_SECONDS: int = 7200
    SESSION_REVIEW_ENABLED: bool = True

    @property
    def redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[4] / ".env",
        env_ignore_missing=True,
        extra="ignore",
    )


settings = Settings()
