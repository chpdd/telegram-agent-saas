import asyncio
from functools import lru_cache
from pathlib import Path

import streamlit as st
from admin_database import async_session_maker
from auth import AUTH_STATUS_KEY, TENANT_ID_KEY, apply_auth
from catalog_seed import import_seed_catalog
from chat_monitor import ACTIVE_CHATS_KEY, add_chat, ensure_chat_state, remove_chat
from core.config import Settings, get_settings
from schema_designer import (
    SCHEMAS_KEY,
    add_column,
    add_schema,
    delete_column,
    delete_schema,
    ensure_schema_state,
    update_column,
    update_schema,
)
from tenant_management import create_tenant, list_tenants

RUNTIME_SETTINGS_KEY = "admin_runtime_settings"
DEFAULT_CATALOG_SEED_PATH = Path(__file__).parents[3] / "data" / "services.json"


def bootstrap_runtime() -> Settings:
    settings = get_settings()
    st.set_page_config(
        page_title="Telegram Chat Agent Admin",
        layout="wide",
    )
    st.session_state.setdefault(RUNTIME_SETTINGS_KEY, settings)
    return settings


@lru_cache(maxsize=1)
def get_admin_event_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def run_async(coro):
    loop = get_admin_event_loop()
    return loop.run_until_complete(coro)


def render_auth() -> None:
    st.title("Dashboard Login")
    st.caption("Введите ID магазина для входа в демо-режиме.")

    tenant_id = st.text_input("ID магазина", key="tenant_id_input")
    if st.button("Войти"):
        if apply_auth(st.session_state, tenant_id):
            st.success("Вход выполнен")
        else:
            st.error("Укажите корректный ID магазина")

    st.divider()
    render_tenant_management()


def render_dashboard() -> None:
    st.header("Панель управления")
    settings = st.session_state[RUNTIME_SETTINGS_KEY]
    st.caption(f"Mode: {settings.MODE}")
    st.info("Демо-режим: доступ ограничен.")
    render_tenant_management()
    render_catalog_seed_import()
    render_schema_designer()
    render_live_chat_monitor()


async def _list_tenants() -> list[dict[str, str | None]]:
    async with async_session_maker() as session:
        return await list_tenants(session)


async def _create_tenant(
    tenant_id: str | None,
    bot_token: str | None,
    system_prompt: str | None,
) -> dict[str, str | None]:
    async with async_session_maker() as session:
        return await create_tenant(
            session,
            tenant_id=tenant_id,
            bot_token=bot_token,
            system_prompt=system_prompt,
        )


async def _import_catalog_seed(tenant_id: str) -> int:
    async with async_session_maker() as session:
        return await import_seed_catalog(
            session,
            tenant_id=tenant_id,
            source_path=DEFAULT_CATALOG_SEED_PATH,
        )


def render_tenant_management() -> None:
    st.subheader("Tenants")
    st.caption("Создание tenant без ручного SQL.")

    tenant_id = st.text_input("Tenant ID (UUID, опционально)")
    bot_token = st.text_input("Bot Token", type="password")
    system_prompt = st.text_area("System Prompt", height=120)

    if st.button("Создать tenant"):
        try:
            created = run_async(_create_tenant(tenant_id, bot_token, system_prompt))
            st.success(f"Tenant создан: {created['tenant_id']}")
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:  # pragma: no cover
            st.error(f"Не удалось создать tenant: {exc}")

    try:
        tenants = run_async(_list_tenants())
    except Exception as exc:  # pragma: no cover
        st.error(f"Не удалось загрузить tenants: {exc}")
        return

    if not tenants:
        st.info("Tenant-ов пока нет.")
        return

    st.dataframe(tenants, use_container_width=True)
    st.divider()


def render_catalog_seed_import() -> None:
    st.subheader("Каталог")
    tenant_id = st.session_state.get(TENANT_ID_KEY, "")
    if not tenant_id:
        st.info("Войди с tenant_id, чтобы импортировать каталог.")
        return

    st.caption(f"Импорт из `{DEFAULT_CATALOG_SEED_PATH.name}` для tenant `{tenant_id}`.")
    if st.button("Импортировать демо-каталог"):
        try:
            imported_count = run_async(_import_catalog_seed(tenant_id))
            st.success(f"Импортировано позиций: {imported_count}")
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:  # pragma: no cover
            st.error(f"Не удалось импортировать каталог: {exc}")
    st.divider()


def render_schema_designer() -> None:
    st.subheader("Каталожные схемы")
    ensure_schema_state(st.session_state)

    schemas = st.session_state[SCHEMAS_KEY]
    options = [f"{idx + 1}. {schema['name']}" for idx, schema in enumerate(schemas)]
    selected_label = st.selectbox(
        "Выберите схему",
        options=options if options else ["(схем нет)"],
        index=0,
    )
    active_index = options.index(selected_label) if options else None

    name = ""
    if active_index is not None:
        active_schema = schemas[active_index]
        name = active_schema["name"]

    form_mode = st.radio("Действие", ["Создать", "Обновить"], horizontal=True)
    input_name = st.text_input("Название схемы", value=name)

    if form_mode == "Создать":
        if st.button("Добавить схему"):
            try:
                add_schema(st.session_state, input_name)
                st.success("Схема добавлена")
            except ValueError as exc:
                st.error(str(exc))
    else:
        if st.button("Сохранить изменения"):
            try:
                if active_index is None:
                    raise ValueError("Выберите схему для обновления")
                update_schema(st.session_state, active_index, input_name)
                st.success("Схема обновлена")
            except (ValueError, IndexError) as exc:
                st.error(str(exc))

        if st.button("Удалить схему"):
            try:
                if active_index is None:
                    raise ValueError("Выберите схему для удаления")
                delete_schema(st.session_state, active_index)
                st.warning("Схема удалена")
            except (ValueError, IndexError) as exc:
                st.error(str(exc))

    st.divider()
    st.subheader("Колонки каталога")
    columns = schemas[active_index]["columns"] if active_index is not None else []
    column_options = [f"{idx + 1}. {col['key']}" for idx, col in enumerate(columns)]
    selected_column = st.selectbox(
        "Выберите колонку",
        options=column_options if column_options else ["(колонок нет)"],
        index=0,
    )
    column_index = column_options.index(selected_column) if column_options else None

    column_key = ""
    column_label = ""
    column_description = ""
    if column_index is not None:
        column = columns[column_index]
        column_key = column["key"]
        column_label = column["label"]
        column_description = column.get("description", "")

    column_mode = st.radio("Колонки", ["Добавить", "Обновить"], horizontal=True, key="columns_mode")
    input_key = st.text_input("Колонка в базе", value=column_key)
    input_label = st.text_input("Название в интерфейсе", value=column_label)
    input_description = st.text_area("Описание", value=column_description, height=120)

    if column_mode == "Добавить":
        if st.button("Добавить колонку"):
            try:
                if active_index is None:
                    raise ValueError("Выберите схему")
                add_column(st.session_state, active_index, input_key, input_label, input_description)
                st.success("Колонка добавлена")
            except (ValueError, IndexError) as exc:
                st.error(str(exc))
    else:
        if st.button("Сохранить колонку"):
            try:
                if active_index is None or column_index is None:
                    raise ValueError("Выберите колонку")
                update_column(
                    st.session_state,
                    active_index,
                    column_index,
                    input_key,
                    input_label,
                    input_description,
                )
                st.success("Колонка обновлена")
            except (ValueError, IndexError) as exc:
                st.error(str(exc))

        if st.button("Удалить колонку"):
            try:
                if active_index is None or column_index is None:
                    raise ValueError("Выберите колонку")
                delete_column(st.session_state, active_index, column_index)
                st.warning("Колонка удалена")
            except (ValueError, IndexError) as exc:
                st.error(str(exc))


def render_live_chat_monitor() -> None:
    st.subheader("Активные чаты")
    ensure_chat_state(st.session_state)
    chats = st.session_state[ACTIVE_CHATS_KEY]
    if not chats:
        st.info("Активных чатов нет.")

    for idx, chat in enumerate(chats):
        cols = st.columns([3, 3, 2, 2])
        cols[0].write(chat["session_id"])
        cols[1].write(chat["user_id"])
        cols[2].write(chat["status"])
        if cols[3].button("Удалить", key=f"chat-remove-{idx}"):
            try:
                remove_chat(st.session_state, idx)
                st.success("Чат удалён")
            except IndexError as exc:
                st.error(str(exc))
            return

    st.divider()
    st.subheader("Добавить чат (мок)")
    session_id = st.text_input("Session ID", key="chat_session_id")
    user_id = st.text_input("User ID", key="chat_user_id")
    status = st.selectbox("Статус", ["open", "closed"], index=0)

    if st.button("Добавить чат"):
        try:
            add_chat(st.session_state, session_id, user_id, status)
            st.success("Чат добавлен")
        except ValueError as exc:
            st.error(str(exc))


def main() -> None:
    bootstrap_runtime()
    if st.session_state.get(AUTH_STATUS_KEY):
        st.sidebar.success(f"Магазин: {st.session_state.get(TENANT_ID_KEY)}")
        render_dashboard()
    else:
        render_auth()


if __name__ == "__main__":
    main()
