from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str = "telegram_ai_agent"
    DB_USER: str = "user"
    DB_PASS: str = "password"
    DB_PORT: int = 5432
    DB_HOST: str = "db"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    MODE: str = "DEV"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=Path(__file__).parents[3] / ".env", env_ignore_missing=True)

settings = Settings()

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
