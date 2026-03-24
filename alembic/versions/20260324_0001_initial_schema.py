"""create initial schema

Revision ID: 20260324_0001
Revises:
Create Date: 2026-03-24 06:05:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260324_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bot_token", sa.String(), nullable=False),
        sa.Column("system_prompt", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bot_token"),
    )

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_tenant_id", "products", ["tenant_id"], unique=False)

    op.create_table(
        "chats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index("ix_chats_tenant_id", "chats", ["tenant_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_tenant_id", "messages", ["tenant_id"], unique=False)
    op.create_index("ix_messages_chat_id", "messages", ["chat_id"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("items", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_tenant_id", "orders", ["tenant_id"], unique=False)
    op.create_index("ix_orders_chat_id", "orders", ["chat_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_orders_chat_id", table_name="orders")
    op.drop_index("ix_orders_tenant_id", table_name="orders")
    op.drop_table("orders")

    op.drop_index("ix_messages_chat_id", table_name="messages")
    op.drop_index("ix_messages_tenant_id", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_chats_tenant_id", table_name="chats")
    op.drop_table("chats")

    op.drop_index("ix_products_tenant_id", table_name="products")
    op.drop_table("products")

    op.drop_table("tenants")
