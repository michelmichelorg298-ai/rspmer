import streamlit as st
import pandas as pd
from ui.api_client import ApiClient, ApiError
from ui.helpers import get_cached_list, invalidate_cache, mark_list_stale, rerun


def render_add_supplier(api_client: ApiClient):
    st.subheader("➕ Ajouter un Fournisseur")

    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom du fournisseur *")
            telephone = st.text_input("Téléphone")

        with col2:
            email = st.text_input("Email")

        notes = st.text_area("Notes")

        if st.form_submit_button("✅ Créer le fournisseur"):
            if not nom.strip():
                st.error("Le nom du fournisseur est obligatoire")
                return

            try:
                payload = {
                    "nom": nom.strip(),
                    "telephone": telephone if telephone.strip() else None,
                    "email": email if email.strip() else None,
                    "notes": notes if notes.strip() else None,
                }
                result = api_client.create_supplier(payload)
                st.success(f"✅ Fournisseur créé avec l'ID {result['id']}")
                mark_list_stale("suppliers")
                rerun()
            except ApiError as e:
                st.error(f"❌ Erreur: {e}")


def render_supplier_list(api_client: ApiClient):
    st.subheader("📋 Liste des Fournisseurs")

    if st.button("🔄 Actualiser", key="refresh_suppliers"):
        mark_list_stale("suppliers")

    try:
        suppliers = get_cached_list("suppliers", api_client.list_suppliers)

        if not suppliers:
            st.info("Aucun fournisseur trouvé")
            return

        df = pd.DataFrame(suppliers)
        cols = ["id", "nom", "telephone", "email", "created_at"]
        display_cols = [c for c in cols if c in df.columns]
        df_display = df[display_cols].copy()
        labels = {"id": "ID", "nom": "Nom", "telephone": "Téléphone", "email": "Email", "created_at": "Créé le"}
        df_display.columns = [labels.get(c, c) for c in display_cols]
        if "Créé le" in df_display.columns:
            df_display["Créé le"] = pd.to_datetime(df_display["Créé le"]).dt.strftime("%d/%m/%Y %H:%M")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as e:
        st.error(f"❌ Erreur: {e}")


def render_edit_supplier(api_client: ApiClient):
    st.subheader("✏️ Modifier un Fournisseur")

    supplier_id = st.number_input("ID du fournisseur à modifier", min_value=1, step=1, key="edit_supplier_id")

    if st.button("📥 Charger les données", key="load_supplier_btn"):
        try:
            st.session_state.current_supplier = api_client.get_supplier(supplier_id)
            st.session_state.current_supplier_id = supplier_id
        except ApiError as e:
            st.error(f"❌ Erreur: {e}")

    if "current_supplier" in st.session_state:
        supplier = st.session_state.current_supplier
        edit_id = st.session_state.get("current_supplier_id", supplier_id)

        with st.form("edit_supplier_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom = st.text_input("Nom du fournisseur *", value=supplier["nom"])
                telephone = st.text_input("Téléphone", value=supplier.get("telephone") or "")

            with col2:
                email = st.text_input("Email", value=supplier.get("email") or "")

            notes = st.text_area("Notes", value=supplier.get("notes") or "")

            if st.form_submit_button("✅ Mettre à jour"):
                try:
                    payload = {
                        "nom": nom.strip(),
                        "telephone": telephone if telephone.strip() else None,
                        "email": email if email.strip() else None,
                        "notes": notes if notes.strip() else None,
                    }
                    api_client.update_supplier(edit_id, payload)
                    st.success("✅ Fournisseur mis à jour")
                    invalidate_cache("current_supplier", "current_supplier_id")
                    mark_list_stale("suppliers")
                    rerun()
                except ApiError as e:
                    st.error(f"❌ Erreur: {e}")


def render_delete_supplier(api_client: ApiClient):
    st.subheader("🗑️ Supprimer un Fournisseur")
    st.caption("Rôle administrateur requis.")

    supplier_id = st.number_input("ID du fournisseur à supprimer", min_value=1, step=1, key="delete_supplier_id")

    if st.button("🗑️ Supprimer", key="btn_delete_supplier"):
        try:
            api_client.delete_supplier(supplier_id)
            st.success("✅ Fournisseur supprimé")
            mark_list_stale("suppliers")
            rerun()
        except ApiError as e:
            if "403" in str(e) or "admin" in str(e).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"❌ Erreur: {e}")
