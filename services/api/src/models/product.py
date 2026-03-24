from __future__ import annotations

from uuid import UUID, uuid4

from core.database import Base
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (Index("ix_products_tenant_id", "tenant_id"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
