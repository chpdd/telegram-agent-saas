from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from core.database import Base
from sqlalchemy import Index, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_tenant_id", "tenant_id"), Index("ix_orders_chat_id", "chat_id"))

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    chat_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    items: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
