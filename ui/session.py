import streamlit as st


def init_session_state() -> None:
    if "auth_token" not in st.session_state:
        st.session_state["auth_token"] = None
    if "logged_email" not in st.session_state:
        st.session_state["logged_email"] = ""

    for list_key in ("products", "customers", "suppliers", "sales", "payments", "expenses"):
        st.session_state.setdefault(f"{list_key}_loaded", False)
