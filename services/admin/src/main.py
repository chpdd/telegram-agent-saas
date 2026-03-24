import streamlit as st
from auth import AUTH_STATUS_KEY, TENANT_ID_KEY, apply_auth


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


def main() -> None:
    if st.session_state.get(AUTH_STATUS_KEY):
        st.sidebar.success(f"Магазин: {st.session_state.get(TENANT_ID_KEY)}")
        render_dashboard()
    else:
        render_auth()


if __name__ == "__main__":
    main()
