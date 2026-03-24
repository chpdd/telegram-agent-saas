from __future__ import annotations

from enum import StrEnum
from uuid import UUID, uuid4

from core.database import Base
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_tenant_id", "tenant_id"), Index("ix_messages_chat_id", "chat_id"))

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    chat_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    role: Mapped[MessageRole] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(nullable=True)
