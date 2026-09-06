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
        label = f"#{f['id']} - {f['nom_produit_texte']} du {f['date_obtenu']} ({f['nom_fournisseur']})"
        options.append(label)
        ids.append(f["id"])

    idx = 0
    if default_id is not None and default_id in ids:
        idx = ids.index(default_id)

    choix = st.selectbox(
        "Fourniture (optionnel)",
        options,
        index=idx,
        key=f"{key_prefix}_fourniture",
    )
    pos = options.index(choix)
    return ids[pos]


def render_add_vente(api_client: ApiClient):
    st.subheader("➕ Ajouter une Vente")

    try:
        products = get_cached_list("products", api_client.list_products)
        fournitures = get_cached_list("fournitures", api_client.list_fournitures)
    except ApiError as e:
        st.error(f"❌ Impossible de charger les références: {e}")
        return

    with st.form("add_vente_form"):
        col1, col2 = st.columns(2)

        with col1:
            date_livraison = st.date_input("Date de livraison *", key="v_date_liv")
            product_id, nom_produit = _product_selector(products, key_prefix="v_add")
            fourniture_id = _fourniture_selector(fournitures, key_prefix="v_add")
            date_obtenu_fourniture = None
            if fourniture_id is not None:
                for f in fournitures:
                    if f["id"] == fourniture_id:
                        try:
                            date_obtenu_fourniture = pd.to_datetime(f["date_obtenu"]).date()
                        except Exception:
                            pass
                        break
            nom_ou_restaurant = st.text_input("Nom / Restaurant *", key="v_nom")

        with col2:
            kilo = st.number_input("Kilos vendus *", min_value=0.0, step=0.1, key="v_kilo")
            prix = st.number_input("Prix total *", min_value=0.0, step=0.5, key="v_prix")
            lieu = st.text_input("Lieu (optionnel)", key="v_lieu")
            numero_telephone = st.text_input("N° téléphone (optionnel)", key="v_tel")

        if st.form_submit_button("✅ Enregistrer la vente"):
            if not nom_produit or not nom_ou_restaurant.strip() or kilo <= 0 or prix <= 0:
                st.error("❌ Champs obligatoires : produit, nom/restaurant, kilo>0, prix>0.")
            else:
                payload = {
                    "product_id": product_id,
                    "nom_produit_texte": nom_produit,
                    "fourniture_id": fourniture_id,
                    "date_obtenu_fourniture": date_obtenu_fourniture.isoformat() if date_obtenu_fourniture else None,
                    "date_livraison": date_livraison.isoformat(),
                    "nom_ou_restaurant": nom_ou_restaurant.strip(),
                    "kilo": kilo,
                    "prix": prix,
                    "lieu": lieu.strip() or None,
                    "numero_telephone": numero_telephone.strip() or None,
                }
                try:
                    result = api_client.create_vente(payload)
                    st.success(f"✅ Vente créée ID {result['id']}")
                    mark_list_stale("ventes")
                    mark_list_stale("products")
                    rerun()
                except ApiError as e:
                    st.error(f"❌ Erreur: {e}")


def render_vente_list(api_client: ApiClient):
    st.subheader("📋 Liste des Ventes")

    if st.button("🔄 Actualiser", key="refresh_ventes"):
        mark_list_stale("ventes")

    try:
        items = get_cached_list("ventes", api_client.list_ventes)

        if not items:
            st.info("Aucune vente. Créez-en une dans l'onglet 'Ajouter'.")
            return

        df = pd.DataFrame(items)
        cols = [
            "id", "date_livraison", "nom_produit_texte", "nom_ou_restaurant",
            "kilo", "prix", "lieu", "numero_telephone", "date_obtenu_fourniture",
        ]
        display_cols = [c for c in cols if c in df.columns]
        df_display = df[display_cols].copy()
        labels = {
            "id": "ID",
            "date_livraison": "Livraison",
            "nom_produit_texte": "Produit",
            "nom_ou_restaurant": "Client/Resto",
            "kilo": "Kg",
            "prix": "Prix",
            "lieu": "Lieu",
            "numero_telephone": "Téléphone",
            "date_obtenu_fourniture": "Date fourniture",
        }
        df_display.columns = [labels.get(c, c) for c in display_cols]
        for dcol in ["Livraison", "Date fourniture"]:
            if dcol in df_display.columns:
                df_display[dcol] = pd.to_datetime(df_display[dcol], errors="coerce").dt.strftime("%d/%m/%Y")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as e:
        st.error(f"❌ Erreur: {e}")


def render_edit_vente(api_client: ApiClient):
    st.subheader("✏️ Modifier une Vente")

    vente_id = st.number_input("ID de la vente à modifier", min_value=1, step=1, key="edit_v_id")
    if st.button("📥 Charger", key="load_v_btn"):
        try:
            st.session_state.current_vente = api_client.get_vente(vente_id)
            st.session_state.current_v_id = vente_id
        except ApiError as e:
            st.error(f"❌ Erreur: {e}")

    if "current_vente" in st.session_state:
        cur = st.session_state.current_vente
        edit_id = st.session_state.get("current_v_id", vente_id)

        try:
            products = get_cached_list("products", api_client.list_products)
            fournitures = get_cached_list("fournitures", api_client.list_fournitures)
        except ApiError as e:
            st.error(f"❌ Impossible de charger les références: {e}")
            return

        with st.form("edit_v_form"):
            col1, col2 = st.columns(2)

            with col1:
                try:
                    dl = pd.to_datetime(cur["date_livraison"]).date()
                except Exception:
                    dl = datetime.now().date()
                date_livraison = st.date_input("Date livraison", value=dl, key="ev_date")
                product_id, nom_produit = _product_selector(
                    products,
                    default_nom=cur.get("nom_produit_texte", ""),
                    default_id=cur.get("product_id"),
                    key_prefix="ev",
                )
                fourniture_id = _fourniture_selector(
                    fournitures,
                    default_id=cur.get("fourniture_id"),
                    key_prefix="ev",
                )
                nom_ou_restaurant = st.text_input(
                    "Nom/Restaurant",
                    value=cur.get("nom_ou_restaurant", ""),
                    key="ev_nom",
                )

            with col2:
                kilo = st.number_input(
                    "Kilos",
                    value=float(cur.get("kilo", 0) or 0),
                    min_value=0.0,
                    step=0.1,
                    key="ev_kilo",
                )
                prix = st.number_input(
                    "Prix",
                    value=float(cur.get("prix", 0) or 0),
                    min_value=0.0,
                    step=0.5,
                    key="ev_prix",
                )
                lieu = st.text_input("Lieu", value=cur.get("lieu") or "", key="ev_lieu")
                numero_telephone = st.text_input("Téléphone", value=cur.get("numero_telephone") or "", key="ev_tel")

            if st.form_submit_button("✅ Mettre à jour"):
                if not nom_produit or not nom_ou_restaurant.strip() or kilo <= 0 or prix <= 0:
                    st.error("❌ Champs obligatoires non remplis.")
                else:
                    payload = {
                        "product_id": product_id,
                        "nom_produit_texte": nom_produit,
                        "fourniture_id": fourniture_id,
                        "date_livraison": date_livraison.isoformat(),
                        "nom_ou_restaurant": nom_ou_restaurant.strip(),
                        "kilo": kilo,
                        "prix": prix,
                        "lieu": lieu.strip() or None,
                        "numero_telephone": numero_telephone.strip() or None,
                    }
                    try:
                        api_client.update_vente(edit_id, payload)
                        st.success("✅ Vente mise à jour")
                        invalidate_cache("current_vente", "current_v_id")
                        mark_list_stale("ventes")
                        mark_list_stale("products")
                        rerun()
                    except ApiError as e:
                        st.error(f"❌ Erreur: {e}")


def render_delete_vente(api_client: ApiClient):
    st.subheader("🗑️ Supprimer une Vente")
    st.caption("Rôle administrateur requis.")

    vente_id = st.number_input("ID à supprimer", min_value=1, step=1, key="del_v_id")
    if st.button("🗑️ Supprimer", key="btn_del_v"):
        try:
            api_client.delete_vente(vente_id)
            st.success(f"✅ Vente {vente_id} supprimée")
            mark_list_stale("ventes")
            mark_list_stale("products")
            rerun()
        except ApiError as e:
            if "403" in str(e) or "admin" in str(e).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"❌ Erreur: {e}")
