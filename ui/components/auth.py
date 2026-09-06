import streamlit as st

from ..api_client import ApiClient, ApiError
from ..helpers import rerun


def render_auth_sidebar(api_url: str) -> ApiClient | None:
    st.sidebar.header("🔐 Authentification")
    login_email = st.sidebar.text_input(
        "Email",
        key="login_email",
        value=st.session_state["logged_email"],
        placeholder="reader@gmail.com",
    )
    login_password = st.sidebar.text_input(
        "Mot de passe",
        type="password",
        key="login_password",
    )
    col1, col2 = st.sidebar.columns(2)

    with col1:
        login_btn = st.button("Se connecter", key="login_btn", use_container_width=True)
    with col2:
        logout_btn = st.button("Déconnecter", key="logout_btn", use_container_width=True)

    if login_btn:
        email = login_email.strip()
        if not email or not login_password:
            st.sidebar.error("Email et mot de passe requis.")
        else:
            client = ApiClient(api_url)
            try:
                token_data = client.login(email, login_password)
                st.session_state["auth_token"] = token_data["access_token"]
                st.session_state["logged_email"] = email
                rerun()
            except ApiError as exc:
                st.sidebar.error(f"Connexion échouée : {exc}")
            except Exception as exc:
                st.sidebar.error(f"Connexion échouée : {exc}")

    if logout_btn:
        st.session_state.pop("auth_token", None)
        st.session_state.pop("logged_email", None)
        for key in list(st.session_state.keys()):
            if key.endswith("_loaded") or key in {
                "products", "customers", "suppliers", "sales", "payments", "expenses",
                "current_product", "current_customer", "current_supplier",
                "current_sale", "current_payment", "update_data",
            }:
                st.session_state.pop(key, None)
        rerun()

    token = st.session_state.get("auth_token")
    if not token:
        st.sidebar.warning("⚠️ Non connecté")
        st.sidebar.info(
            "**Comptes de test :**\n"
            "- reader@gmail.com / readerpass\n"
            "- writer@gmail.com / writerpass\n"
            "- admin@gmail.com / adminpass"
        )
        return None

    st.sidebar.success(f"👤 Connecté : {st.session_state.get('logged_email', 'Utilisateur')}")
    return ApiClient(api_url, token=token)
