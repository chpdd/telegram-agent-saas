from __future__ import annotations

from enum import StrEnum
from uuid import UUID, uuid4

from core.database import Base
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class ChatStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = (Index("ix_chats_tenant_id", "tenant_id"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    session_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    status: Mapped[ChatStatus] = mapped_column(nullable=False, default=ChatStatus.OPEN)
    user_id: Mapped[str] = mapped_column(nullable=False)
