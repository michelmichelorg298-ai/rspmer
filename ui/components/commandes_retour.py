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
SELECTION_VIDE = "— Aucun —"


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
        )
        nom_produit = valeur_autre.strip()
        product_id = None
    else:
        matching = next((p for p in products if p["nom"] == choix), None)
        product_id = matching["id"] if matching else None
        nom_produit = choix

    return product_id, nom_produit


def _fourniture_selector(
    fournitures: list,
    default_id: int | None = None,
    key_prefix: str = "fsel",
) -> int | None:
    options = [SELECTION_VIDE]
    ids = [None]
    for f in fournitures:
        label = f"#{f['id']} - {f['nom_produit_texte']} du {f['date_obtenu']}"
        options.append(label)
        ids.append(f["id"])

    idx = 0
    if default_id is not None and default_id in ids:
        idx = ids.index(default_id)

    choix = st.selectbox(
        "Fourniture liée (optionnel)",
        options,
        index=idx,
        key=f"{key_prefix}_fourniture",
    )
    pos = options.index(choix)
    return ids[pos]


def render_add_commande_retour(api_client: ApiClient):
    st.subheader("➕ Ajouter un Retour")

    try:
        products = get_cached_list("products", api_client.list_products)
        fournitures = get_cached_list("fournitures", api_client.list_fournitures)
    except ApiError as e:
        st.error(f"❌ Impossible de charger les références: {e}")
        return

    with st.form("add_retour_form"):
        col1, col2 = st.columns(2)

        with col1:
            product_id, nom_produit = _product_selector(products, key_prefix="r_add")
            fourniture_id = _fourniture_selector(fournitures, key_prefix="r_add")
            origine = st.text_input("Origine *", key="r_origine", placeholder="Ex: Conakry")
            kilo = st.number_input("Kilos retournés *", min_value=0.0, step=0.1, key="r_kilo")

        with col2:
            cause = st.text_area("Cause du retour *", key="r_cause", height=150, placeholder="Ex: Produit périmé, qualité insuffisante...")

        if st.form_submit_button("✅ Enregistrer le retour"):
            if not nom_produit or not origine.strip() or kilo <= 0 or not cause.strip():
                st.error("❌ Champs obligatoires : produit, origine, kilo>0, cause.")
            else:
                payload = {
                    "product_id": product_id,
                    "nom_produit_texte": nom_produit,
                    "fourniture_id": fourniture_id,
                    "origine": origine.strip(),
                    "kilo": kilo,
                    "cause": cause.strip(),
                }
                try:
                    result = api_client.create_commande_retour(payload)
                    st.success(f"✅ Retour créé ID {result['id']}")
                    mark_list_stale("commandes_retour")
                    mark_list_stale("products")
                    rerun()
                except ApiError as e:
                    st.error(f"❌ Erreur: {e}")


def render_commande_retour_list(api_client: ApiClient):
    st.subheader("📋 Liste des Retours")

    if st.button("🔄 Actualiser", key="refresh_retours"):
        mark_list_stale("commandes_retour")

    try:
        items = get_cached_list("commandes_retour", api_client.list_commandes_retour)

        if not items:
            st.info("Aucun retour enregistré.")
            return

        df = pd.DataFrame(items)
        cols = ["id", "nom_produit_texte", "origine", "kilo", "cause", "created_at"]
        display_cols = [c for c in cols if c in df.columns]
        df_display = df[display_cols].copy()
        labels = {
            "id": "ID",
            "nom_produit_texte": "Produit",
            "origine": "Origine",
            "kilo": "Kg",
            "cause": "Cause",
            "created_at": "Enregistré le",
        }
        df_display.columns = [labels.get(c, c) for c in display_cols]
        if "Enregistré le" in df_display.columns:
            df_display["Enregistré le"] = pd.to_datetime(df_display["Enregistré le"], errors="coerce").dt.strftime("%d/%m/%Y %H:%M")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as e:
        st.error(f"❌ Erreur: {e}")


def render_edit_commande_retour(api_client: ApiClient):
    st.subheader("✏️ Modifier un Retour")

    retour_id = st.number_input("ID du retour à modifier", min_value=1, step=1, key="edit_r_id")
    if st.button("📥 Charger", key="load_r_btn"):
        try:
            st.session_state.current_retour = api_client.get_commande_retour(retour_id)
            st.session_state.current_r_id = retour_id
        except ApiError as e:
            st.error(f"❌ Erreur: {e}")

    if "current_retour" in st.session_state:
        cur = st.session_state.current_retour
        edit_id = st.session_state.get("current_r_id", retour_id)

        try:
            products = get_cached_list("products", api_client.list_products)
            fournitures = get_cached_list("fournitures", api_client.list_fournitures)
        except ApiError as e:
            st.error(f"❌ Impossible de charger les références: {e}")
            return

        with st.form("edit_r_form"):
            col1, col2 = st.columns(2)

            with col1:
                product_id, nom_produit = _product_selector(
                    products,
                    default_nom=cur.get("nom_produit_texte", ""),
                    default_id=cur.get("product_id"),
                    key_prefix="er",
                )
                fourniture_id = _fourniture_selector(
                    fournitures,
                    default_id=cur.get("fourniture_id"),
                    key_prefix="er",
                )
                origine = st.text_input("Origine", value=cur.get("origine", ""), key="er_origine")
                kilo = st.number_input(
                    "Kilos",
                    value=float(cur.get("kilo", 0) or 0),
                    min_value=0.0,
                    step=0.1,
                    key="er_kilo",
                )

            with col2:
                cause = st.text_area(
                    "Cause",
                    value=cur.get("cause", ""),
                    key="er_cause",
                    height=200,
                )

            if st.form_submit_button("✅ Mettre à jour"):
                if not nom_produit or not origine.strip() or kilo <= 0 or not cause.strip():
                    st.error("❌ Champs obligatoires non remplis.")
                else:
                    payload = {
                        "product_id": product_id,
                        "nom_produit_texte": nom_produit,
                        "fourniture_id": fourniture_id,
                        "origine": origine.strip(),
                        "kilo": kilo,
                        "cause": cause.strip(),
                    }
                    try:
                        api_client.update_commande_retour(edit_id, payload)
                        st.success("✅ Retour mis à jour")
                        invalidate_cache("current_retour", "current_r_id")
                        mark_list_stale("commandes_retour")
                        mark_list_stale("products")
                        rerun()
                    except ApiError as e:
                        st.error(f"❌ Erreur: {e}")


def render_delete_commande_retour(api_client: ApiClient):
    st.subheader("🗑️ Supprimer un Retour")
    st.caption("Rôle administrateur requis.")

    retour_id = st.number_input("ID à supprimer", min_value=1, step=1, key="del_r_id")
    if st.button("🗑️ Supprimer", key="btn_del_r"):
        try:
            api_client.delete_commande_retour(retour_id)
            st.success(f"✅ Retour {retour_id} supprimé")
            mark_list_stale("commandes_retour")
            mark_list_stale("products")
            rerun()
        except ApiError as e:
            if "403" in str(e) or "admin" in str(e).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"❌ Erreur: {e}")
