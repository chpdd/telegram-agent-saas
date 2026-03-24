import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from core.database import Base  # noqa: E402
from crud.base import BaseCRUD, SchemaCRUD  # noqa: E402


class DummyTenantModel(Base):
    __tablename__ = "dummy_tenant_crud"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(default="")


class CreateSchema(BaseModel):
    name: str


class UpdateSchema(BaseModel):
    name: str | None = None


class FakeResult:
    def __init__(self, items):
        self._items = list(items)

    def scalars(self):
        return self

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return list(self._items)


def _make_session(result, mocker):
    session = SimpleNamespace()
    session.execute = mocker.AsyncMock(return_value=result)
    session.commit = mocker.AsyncMock()
    session.refresh = mocker.AsyncMock()
    session.add = mocker.MagicMock()
    return session


def _compiled_sql(statement):
    return str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


@pytest.mark.asyncio
async def test_base_crud_get_includes_tenant_filter(mocker):
    tenant_id = uuid4()
    item = DummyTenantModel(id=uuid4(), tenant_id=tenant_id, name="test")
    session = _make_session(FakeResult([item]), mocker)

    crud = BaseCRUD(DummyTenantModel)
    result = await crud.get(session, tenant_id, item.id)

    stmt = session.execute.call_args.args[0]
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql
    assert str(tenant_id) in sql
    assert result is item


@pytest.mark.asyncio
async def test_base_crud_list_includes_tenant_filter(mocker):
    tenant_id = uuid4()
    item = DummyTenantModel(id=uuid4(), tenant_id=tenant_id, name="test")
    session = _make_session(FakeResult([item]), mocker)

    crud = BaseCRUD(DummyTenantModel)
    results = await crud.list(session, tenant_id, offset=0, limit=10)

    stmt = session.execute.call_args.args[0]
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql
    assert str(tenant_id) in sql
    assert results == [item]


@pytest.mark.asyncio
async def test_base_crud_create_sets_tenant_and_commits(mocker):
    tenant_id = uuid4()
    session = _make_session(FakeResult([]), mocker)

    crud = BaseCRUD(DummyTenantModel)
    result = await crud.create(session, tenant_id, {"name": "new"})

    assert result.tenant_id == tenant_id
    assert result.name == "new"
    session.add.assert_called_once_with(result)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_base_crud_update_ignores_tenant_id_changes(mocker):
    tenant_id = uuid4()
    other_tenant = uuid4()
    item = DummyTenantModel(id=uuid4(), tenant_id=tenant_id, name="updated")
    session = _make_session(FakeResult([item]), mocker)

    crud = BaseCRUD(DummyTenantModel)
    result = await crud.update(session, tenant_id, item.id, {"name": "updated", "tenant_id": other_tenant})

    stmt = session.execute.call_args.args[0]
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql
    assert str(tenant_id) in sql
    assert str(other_tenant) not in sql
    assert "set tenant_id" not in sql.lower()
    assert result is item


@pytest.mark.asyncio
async def test_base_crud_delete_includes_tenant_filter(mocker):
    tenant_id = uuid4()
    item = DummyTenantModel(id=uuid4(), tenant_id=tenant_id, name="deleted")
    session = _make_session(FakeResult([item]), mocker)

    crud = BaseCRUD(DummyTenantModel)
    result = await crud.delete(session, tenant_id, item.id)

    stmt = session.execute.call_args.args[0]
    sql = _compiled_sql(stmt)
    assert "tenant_id" in sql
    assert str(tenant_id) in sql
    assert result is item


@pytest.mark.asyncio
async def test_schema_crud_uses_pydantic_models(mocker):
    tenant_id = uuid4()
    session = _make_session(FakeResult([]), mocker)

    crud = SchemaCRUD[DummyTenantModel, CreateSchema, UpdateSchema](DummyTenantModel)
    result = await crud.create(session, tenant_id, CreateSchema(name="from-schema"))

    assert result.name == "from-schema"
    assert result.tenant_id == tenant_id
