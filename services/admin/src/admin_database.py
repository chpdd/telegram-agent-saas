from collections.abc import Generator

from core.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

settings = get_settings()

sync_database_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg")

engine = create_engine(
    sync_database_url,
    pool_pre_ping=True,
)

session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


def get_session() -> Generator[Session, None, None]:
    with session_maker() as session:
        yield session
