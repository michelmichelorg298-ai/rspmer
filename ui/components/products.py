import streamlit as st
import pandas as pd
from ui.api_client import ApiClient, ApiError
from ui.helpers import get_cached_list, invalidate_cache, mark_list_stale, rerun, safe_index

CATEGORIES = ["Autre", "Poisson", "Fruits de mer", "Crustacés", "Conserves"]


def render_add_product(api_client: ApiClient):
    st.subheader("➕ Ajouter un Produit")

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom du produit *")
            categorie = st.selectbox("Catégorie", CATEGORIES)
            prix_achat = st.number_input("Prix d'achat référence (kg)", min_value=0.0, step=0.01)

        with col2:
            stock_kg = st.number_input("Stock initial (kg)", min_value=0.0, step=0.1)
            seuil_alerte = st.number_input("Seuil d'alerte (kg)", min_value=0.0, step=0.1)

        notes = st.text_area("Notes")

        if st.form_submit_button("✅ Créer le produit"):
            if not nom.strip():
                st.error("Le nom du produit est obligatoire")
                return

            try:
                payload = {
                    "nom": nom.strip(),
                    "categorie": categorie,
                    "prix_achat_ref": prix_achat if prix_achat > 0 else None,
                    "stock_kg": stock_kg,
                    "seuil_alerte_kg": seuil_alerte,
                    "notes": notes if notes.strip() else None,
                }
                result = api_client.create_product(payload)
                st.success(f"✅ Produit créé avec l'ID {result['id']}")
                mark_list_stale("products")
                rerun()
            except ApiError as e:
                error_msg = str(e).lower()
                if "unique" in error_msg or "dupliqu" in error_msg or "ix_products_nom" in error_msg:
                    st.error("❌ Ce nom de produit existe déjà.")
                else:
                    st.error(f"❌ Erreur: {e}")


def render_product_list(api_client: ApiClient):
    st.subheader("📋 Liste des Produits")

    if st.button("🔄 Actualiser", key="refresh_products"):
        mark_list_stale("products")

    try:
        products = get_cached_list("products", api_client.list_products)

        if not products:
            st.info("Aucun produit trouvé. Créez-en un depuis l'onglet 'Ajouter'.")
            return

        df = pd.DataFrame(products)
        cols = ["id", "nom", "categorie", "stock_kg", "seuil_alerte_kg", "prix_achat_ref", "created_at"]
        display_cols = [c for c in cols if c in df.columns]
        df_display = df[display_cols].copy()
        labels = {
            "id": "ID",
            "nom": "Nom",
            "categorie": "Catégorie",
            "stock_kg": "Stock (kg)",
            "seuil_alerte_kg": "Seuil alerte (kg)",
            "prix_achat_ref": "Prix achat",
            "created_at": "Créé le",
        }
        df_display.columns = [labels.get(c, c) for c in display_cols]
        if "Créé le" in df_display.columns:
            df_display["Créé le"] = pd.to_datetime(df_display["Créé le"]).dt.strftime("%d/%m/%Y %H:%M")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as e:
        st.error(f"❌ Erreur lors de la récupération: {e}")


def render_edit_product(api_client: ApiClient):
    st.subheader("✏️ Modifier un Produit")

    product_id = st.number_input("ID du produit à modifier", min_value=1, step=1, key="edit_product_id")

    if st.button("📥 Charger les données", key="load_product_btn"):
        try:
            st.session_state.current_product = api_client.get_product(product_id)
            st.session_state.current_product_id = product_id
        except ApiError as e:
            st.error(f"❌ Erreur: {e}")

    if "current_product" in st.session_state:
        product = st.session_state.current_product
        edit_id = st.session_state.get("current_product_id", product_id)

        with st.form("edit_product_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom = st.text_input("Nom du produit *", value=product["nom"])
                categorie = st.selectbox(
                    "Catégorie",
                    CATEGORIES,
                    index=safe_index(CATEGORIES, product.get("categorie"), 0),
                )
                prix_achat = st.number_input(
                    "Prix d'achat référence (kg)",
                    value=float(product.get("prix_achat_ref") or 0.0),
                    step=0.01,
                )

            with col2:
                stock_kg = st.number_input("Stock (kg)", value=float(product["stock_kg"]), step=0.1)
                seuil_alerte = st.number_input(
                    "Seuil d'alerte (kg)",
                    value=float(product["seuil_alerte_kg"]),
                    step=0.1,
                )

            notes = st.text_area("Notes", value=product.get("notes") or "")

            if st.form_submit_button("✅ Mettre à jour"):
                try:
                    payload = {
                        "nom": nom.strip(),
                        "categorie": categorie,
                        "prix_achat_ref": prix_achat if prix_achat > 0 else None,
                        "stock_kg": stock_kg,
                        "seuil_alerte_kg": seuil_alerte,
                        "notes": notes if notes.strip() else None,
                    }
                    api_client.update_product(edit_id, payload)
                    st.success("✅ Produit mis à jour")
                    invalidate_cache("current_product", "current_product_id")
                    mark_list_stale("products")
                    rerun()
                except ApiError as e:
                    st.error(f"❌ Erreur: {e}")


def render_delete_product(api_client: ApiClient):
    st.subheader("🗑️ Supprimer un Produit")
    st.caption("Rôle administrateur requis.")

    product_id = st.number_input("ID du produit à supprimer", min_value=1, step=1, key="delete_product_id")

    if st.button("🗑️ Supprimer", key="btn_delete_product"):
        try:
            api_client.delete_product(product_id)
            st.success("✅ Produit supprimé")
            mark_list_stale("products")
            rerun()
        except ApiError as e:
            if "403" in str(e) or "admin" in str(e).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"❌ Erreur: {e}")
