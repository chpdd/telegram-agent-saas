from __future__ import annotations

from uuid import UUID, uuid4

from core.database import Base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    bot_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    system_prompt: Mapped[str | None] = mapped_column(nullable=True)
