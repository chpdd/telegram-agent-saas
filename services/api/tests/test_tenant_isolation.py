import os
import sys
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

os.environ.setdefault("LLM_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from core.database import Base  # noqa: E402
from core.tenancy import TenantScopeError, apply_tenant_filter  # noqa: E402


class DummyTenantModel(Base):
    __tablename__ = "dummy_tenant"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)


class DummyNoTenantModel(Base):
    __tablename__ = "dummy_no_tenant"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)


def _compiled_sql(statement):
    return str(statement.compile(compile_kwargs={"literal_binds": True}))


def test_apply_tenant_filter_select():
    tenant_id = uuid4()
    stmt = apply_tenant_filter(select(DummyTenantModel), DummyTenantModel, tenant_id)
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql
    assert tenant_id.hex in sql


def test_apply_tenant_filter_update():
    tenant_id = uuid4()
    stmt = apply_tenant_filter(update(DummyTenantModel), DummyTenantModel, tenant_id)
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql
    assert tenant_id.hex in sql


def test_apply_tenant_filter_delete():
    tenant_id = uuid4()
    stmt = apply_tenant_filter(delete(DummyTenantModel), DummyTenantModel, tenant_id)
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql
    assert tenant_id.hex in sql


def test_apply_tenant_filter_requires_tenant_id():
    with pytest.raises(TenantScopeError):
        apply_tenant_filter(select(DummyTenantModel), DummyTenantModel, None)


def test_apply_tenant_filter_requires_tenant_column():
    with pytest.raises(TenantScopeError):
        apply_tenant_filter(select(DummyNoTenantModel), DummyNoTenantModel, uuid4())
