import json

import streamlit as st
from auth import AUTH_STATUS_KEY, TENANT_ID_KEY, apply_auth
from schema_designer import (
    SCHEMAS_KEY,
    add_schema,
    delete_schema,
    ensure_schema_state,
    parse_schema_payload,
    update_schema,
)


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
    st.info("Демо-режим: доступ ограничен.")
    render_schema_designer()


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
    payload_text = ""
    if active_index is not None:
        active_schema = schemas[active_index]
        name = active_schema["name"]
        payload_text = json.dumps(active_schema["payload"], ensure_ascii=False, indent=2)

    form_mode = st.radio("Действие", ["Создать", "Обновить"], horizontal=True)
    input_name = st.text_input("Название схемы", value=name)
    input_payload = st.text_area("JSON схема", value=payload_text, height=200)

    if form_mode == "Создать":
        if st.button("Добавить схему"):
            try:
                payload = parse_schema_payload(input_payload)
                add_schema(st.session_state, input_name, payload)
                st.success("Схема добавлена")
            except ValueError as exc:
                st.error(str(exc))
    else:
        if st.button("Сохранить изменения"):
            try:
                if active_index is None:
                    raise ValueError("Выберите схему для обновления")
                payload = parse_schema_payload(input_payload)
                update_schema(st.session_state, active_index, input_name, payload)
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


def main() -> None:
    if st.session_state.get(AUTH_STATUS_KEY):
        st.sidebar.success(f"Магазин: {st.session_state.get(TENANT_ID_KEY)}")
        render_dashboard()
    else:
        render_auth()


if __name__ == "__main__":
    main()
