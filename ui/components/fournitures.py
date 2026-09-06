from datetime import datetime

import pandas as pd
import streamlit as st

from ui.api_client import ApiClient, ApiError
from ui.helpers import (
    get_cached_list,
    invalidate_cache,
    mark_list_stale,
    rerun,
    safe_index,
)

AUTRE_LABEL = "➕ Autre..."


def _product_selector(
    products: list,
    default_nom: str | None = None,
    default_id: int | None = None,
    key_prefix: str = "product",
) -> tuple[int | None, str]:
    noms = [p["nom"] for p in products] + [AUTRE_LABEL]
    default_nom = (default_nom or "").strip()

    if default_id is not None:
        for p in products:
            if p["id"] == default_id:
                default_nom = p["nom"]
                break

    if default_nom and default_nom in [p["nom"] for p in products]:
        index_initial = noms.index(default_nom)
    else:
        index_initial = len(noms) - 1

    choix = st.selectbox(
        "Produit (référence)",
        noms,
        index=index_initial,
        key=f"{key_prefix}_select",
    )

    if choix == AUTRE_LABEL:
        valeur_autre = st.text_input(
            "Nom du produit (texte libre)",
            value=default_nom if default_nom and default_nom not in [p["nom"] for p in products] else "",
            key=f"{key_prefix}_autre",
            placeholder="Ex: Crevettes, Homard...",
        )
        nom_produit = valeur_autre.strip()
        product_id = None
    else:
        matching = next((p for p in products if p["nom"] == choix), None)
        product_id = matching["id"] if matching else None
        nom_produit = choix

    return product_id, nom_produit


def render_add_fourniture(api_client: ApiClient):
    st.subheader("➕ Ajouter une Fourniture")

    try:
        products = get_cached_list("products", api_client.list_products)
    except ApiError as e:
        st.error(f"❌ Impossible de charger les produits: {e}")
        return

    with st.form("add_fourniture_form"):
        col1, col2 = st.columns(2)

        with col1:
            date_obtenu = st.date_input("Date obtenu *", key="f_date_obtenu")
            product_id, nom_produit = _product_selector(
                products, key_prefix="f_add"
            )
            origine = st.text_input("Origine *", key="f_origine", placeholder="Ex: Conakry, Casablanca...")
            nom_fournisseur = st.text_input("Nom du fournisseur *", key="f_nom_fournisseur")

        with col2:
            kilo_produit = st.number_input("Kilos de produit *", min_value=0.0, step=0.1, key="f_kilo")
            prix_par_kg = st.number_input("Prix par kg *", min_value=0.0, step=0.05, key="f_prix_kg")

        if st.form_submit_button("✅ Enregistrer la fourniture"):
            if not nom_produit or not origine.strip() or not nom_fournisseur.strip() or kilo_produit <= 0 or prix_par_kg <= 0:
                st.error("❌ Tous les champs marqués sont obligatoires (kilo et prix > 0).")
            else:
                payload = {
                    "product_id": product_id,
                    "nom_produit_texte": nom_produit,
                    "date_obtenu": date_obtenu.isoformat(),
                    "origine": origine.strip(),
                    "nom_fournisseur": nom_fournisseur.strip(),
                    "kilo_produit": kilo_produit,
                    "prix_par_kg": prix_par_kg,
                }
                try:
                    result = api_client.create_fourniture(payload)
                    st.success(f"✅ Fourniture créée ID {result['id']}")
                    mark_list_stale("fournitures")
                    mark_list_stale("products")
                    rerun()
                except ApiError as e:
                    st.error(f"❌ Erreur: {e}")


def render_fourniture_list(api_client: ApiClient):
    st.subheader("📋 Liste des Fournitures")

    if st.button("🔄 Actualiser", key="refresh_fournitures"):
        mark_list_stale("fournitures")

    try:
        items = get_cached_list("fournitures", api_client.list_fournitures)

        if not items:
            st.info("Aucune fourniture. Créez-en une dans l'onglet 'Ajouter'.")
            return

        df = pd.DataFrame(items)
        cols = [
            "id", "date_obtenu", "nom_produit_texte", "nom_fournisseur",
            "origine", "kilo_produit", "prix_par_kg", "created_at",
        ]
        display_cols = [c for c in cols if c in df.columns]
        df_display = df[display_cols].copy()
        labels = {
            "id": "ID",
            "date_obtenu": "Date",
            "nom_produit_texte": "Produit",
            "nom_fournisseur": "Fournisseur",
            "origine": "Origine",
            "kilo_produit": "Kg",
            "prix_par_kg": "Prix/kg",
            "created_at": "Créé le",
        }
        df_display.columns = [labels.get(c, c) for c in display_cols]
        for dcol in ["Date", "Créé le"]:
            if dcol in df_display.columns:
                df_display[dcol] = pd.to_datetime(df_display[dcol]).dt.strftime("%d/%m/%Y")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as e:
        st.error(f"❌ Erreur: {e}")


def render_edit_fourniture(api_client: ApiClient):
    st.subheader("✏️ Modifier une Fourniture")

    fourniture_id = st.number_input("ID de la fourniture à modifier", min_value=1, step=1, key="edit_f_id")
    if st.button("📥 Charger", key="load_f_btn"):
        try:
            st.session_state.current_fourniture = api_client.get_fourniture(fourniture_id)
            st.session_state.current_f_id = fourniture_id
        except ApiError as e:
            st.error(f"❌ Erreur: {e}")

    if "current_fourniture" in st.session_state:
        cur = st.session_state.current_fourniture
        edit_id = st.session_state.get("current_f_id", fourniture_id)

        try:
            products = get_cached_list("products", api_client.list_products)
        except ApiError as e:
            st.error(f"❌ Impossible de charger les produits: {e}")
            return

        with st.form("edit_f_form"):
            col1, col2 = st.columns(2)

            with col1:
                try:
                    default_date = pd.to_datetime(cur["date_obtenu"]).date()
                except Exception:
                    default_date = datetime.now().date()
                date_obtenu = st.date_input("Date obtenu", value=default_date, key="ef_date")
                product_id, nom_produit = _product_selector(
                    products,
                    default_nom=cur.get("nom_produit_texte", ""),
                    default_id=cur.get("product_id"),
                    key_prefix="ef",
                )
                origine = st.text_input("Origine", value=cur.get("origine", ""), key="ef_origine")
                nom_fournisseur = st.text_input("Nom fournisseur", value=cur.get("nom_fournisseur", ""), key="ef_fourn")

            with col2:
                kilo_produit = st.number_input(
                    "Kilos",
                    value=float(cur.get("kilo_produit", 0) or 0),
                    min_value=0.0,
                    step=0.1,
                    key="ef_kilo",
                )
                prix_par_kg = st.number_input(
                    "Prix/kg",
                    value=float(cur.get("prix_par_kg", 0) or 0),
                    min_value=0.0,
                    step=0.05,
                    key="ef_prix",
                )

            if st.form_submit_button("✅ Mettre à jour"):
                if not nom_produit or not origine.strip() or not nom_fournisseur.strip() or kilo_produit <= 0 or prix_par_kg <= 0:
                    st.error("❌ Tous les champs obligatoires doivent être remplis.")
                else:
                    payload = {
                        "product_id": product_id,
                        "nom_produit_texte": nom_produit,
                        "date_obtenu": date_obtenu.isoformat(),
                        "origine": origine.strip(),
                        "nom_fournisseur": nom_fournisseur.strip(),
                        "kilo_produit": kilo_produit,
                        "prix_par_kg": prix_par_kg,
                    }
                    try:
                        api_client.update_fourniture(edit_id, payload)
                        st.success("✅ Fourniture mise à jour")
                        invalidate_cache("current_fourniture", "current_f_id")
                        mark_list_stale("fournitures")
                        mark_list_stale("products")
                        rerun()
                    except ApiError as e:
                        st.error(f"❌ Erreur: {e}")


def render_delete_fourniture(api_client: ApiClient):
    st.subheader("🗑️ Supprimer une Fourniture")
    st.caption("Rôle administrateur requis.")

    fourniture_id = st.number_input("ID à supprimer", min_value=1, step=1, key="del_f_id")
    if st.button("🗑️ Supprimer", key="btn_del_f"):
        try:
            api_client.delete_fourniture(fourniture_id)
            st.success(f"✅ Fourniture {fourniture_id} supprimée")
            mark_list_stale("fournitures")
            mark_list_stale("products")
            rerun()
        except ApiError as e:
            if "403" in str(e) or "admin" in str(e).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"❌ Erreur: {e}")
