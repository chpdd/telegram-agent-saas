import streamlit as st
from auth import AUTH_STATUS_KEY, TENANT_ID_KEY, apply_auth
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

RUNTIME_SETTINGS_KEY = "admin_runtime_settings"


def bootstrap_runtime() -> Settings:
    settings = get_settings()
    st.set_page_config(
        page_title="Telegram Chat Agent Admin",
        layout="wide",
    )
    st.session_state.setdefault(RUNTIME_SETTINGS_KEY, settings)
    return settings


def render_auth() -> None:
    st.title("Dashboard Login")
    st.caption("Введите ID магазина для входа в демо-режиме.")

    tenant_id = st.text_input("ID магазина", key="tenant_id_input")
    if st.button("Войти"):
        if apply_auth(st.session_state, tenant_id):
            st.success("Вход выполнен")
        else:
            st.error("Укажите корректный ID магазина")


def render_dashboard() -> None:
    st.header("Панель управления")
    settings = st.session_state[RUNTIME_SETTINGS_KEY]
    st.caption(f"Mode: {settings.MODE}")
    st.info("Демо-режим: доступ ограничен.")
    render_schema_designer()
    render_live_chat_monitor()


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
