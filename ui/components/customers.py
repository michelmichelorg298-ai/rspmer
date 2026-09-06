import streamlit as st
import pandas as pd
from ui.api_client import ApiClient, ApiError
from ui.helpers import get_cached_list, invalidate_cache, mark_list_stale, rerun, safe_index

TYPES_CLIENT = ["Particulier", "Restaurant", "Magasin", "Autre"]


def render_add_customer(api_client: ApiClient):
    st.subheader("➕ Ajouter un Client")

    with st.form("add_customer_form"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom du client *")
            type_client = st.selectbox("Type de client", TYPES_CLIENT)
            telephone = st.text_input("Téléphone")

        with col2:
            email = st.text_input("Email")
            conditions_paiement = st.number_input("Conditions paiement (jours)", min_value=0, step=1)

        adresse = st.text_area("Adresse")
        notes = st.text_area("Notes")

        if st.form_submit_button("✅ Créer le client"):
            if not nom.strip():
                st.error("Le nom du client est obligatoire")
                return

            try:
                payload = {
                    "nom": nom.strip(),
                    "type_client": type_client,
                    "telephone": telephone if telephone.strip() else None,
                    "email": email if email.strip() else None,
                    "adresse": adresse if adresse.strip() else None,
                    "conditions_paiement_jours": conditions_paiement,
                    "notes": notes if notes.strip() else None,
                }
                result = api_client.create_customer(payload)
                st.success(f"✅ Client créé avec l'ID {result['id']}")
                mark_list_stale("customers")
                rerun()
            except ApiError as e:
                st.error(f"❌ Erreur: {e}")


def render_customer_list(api_client: ApiClient):
    st.subheader("📋 Liste des Clients")

    if st.button("🔄 Actualiser", key="refresh_customers"):
        mark_list_stale("customers")

    try:
        customers = get_cached_list("customers", api_client.list_customers)

        if not customers:
            st.info("Aucun client trouvé")
            return

        df = pd.DataFrame(customers)
        cols = ["id", "nom", "type_client", "telephone", "email", "encours_actuel", "created_at"]
        display_cols = [c for c in cols if c in df.columns]
        df_display = df[display_cols].copy()
        labels = {
            "id": "ID",
            "nom": "Nom",
            "type_client": "Type",
            "telephone": "Téléphone",
            "email": "Email",
            "encours_actuel": "Encours €",
            "created_at": "Créé le",
        }
        df_display.columns = [labels.get(c, c) for c in display_cols]
        if "Créé le" in df_display.columns:
            df_display["Créé le"] = pd.to_datetime(df_display["Créé le"]).dt.strftime("%d/%m/%Y %H:%M")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as e:
        st.error(f"❌ Erreur: {e}")


def render_edit_customer(api_client: ApiClient):
    st.subheader("✏️ Modifier un Client")

    customer_id = st.number_input("ID du client à modifier", min_value=1, step=1, key="edit_customer_id")

    if st.button("📥 Charger les données", key="load_customer_btn"):
        try:
            st.session_state.current_customer = api_client.get_customer(customer_id)
            st.session_state.current_customer_id = customer_id
        except ApiError as e:
            st.error(f"❌ Erreur: {e}")

    if "current_customer" in st.session_state:
        customer = st.session_state.current_customer
        edit_id = st.session_state.get("current_customer_id", customer_id)

        with st.form("edit_customer_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom = st.text_input("Nom du client *", value=customer["nom"])
                type_client = st.selectbox(
                    "Type de client",
                    TYPES_CLIENT,
                    index=safe_index(TYPES_CLIENT, customer.get("type_client"), 0),
                )
                telephone = st.text_input("Téléphone", value=customer.get("telephone") or "")

            with col2:
                email = st.text_input("Email", value=customer.get("email") or "")
                conditions_paiement = st.number_input(
                    "Conditions paiement (jours)",
                    value=int(customer.get("conditions_paiement_jours") or 0),
                    step=1,
                )

            adresse = st.text_area("Adresse", value=customer.get("adresse") or "")
            notes = st.text_area("Notes", value=customer.get("notes") or "")

            if st.form_submit_button("✅ Mettre à jour"):
                try:
                    payload = {
                        "nom": nom.strip(),
                        "type_client": type_client,
                        "telephone": telephone if telephone.strip() else None,
                        "email": email if email.strip() else None,
                        "adresse": adresse if adresse.strip() else None,
                        "conditions_paiement_jours": conditions_paiement,
                        "notes": notes if notes.strip() else None,
                    }
                    api_client.update_customer(edit_id, payload)
                    st.success("✅ Client mis à jour")
                    invalidate_cache("current_customer", "current_customer_id")
                    mark_list_stale("customers")
                    rerun()
                except ApiError as e:
                    st.error(f"❌ Erreur: {e}")


def render_delete_customer(api_client: ApiClient):
    st.subheader("🗑️ Supprimer un Client")
    st.caption("Rôle administrateur requis.")

    customer_id = st.number_input("ID du client à supprimer", min_value=1, step=1, key="delete_customer_id")

    if st.button("🗑️ Supprimer", key="btn_delete_customer"):
        try:
            api_client.delete_customer(customer_id)
            st.success("✅ Client supprimé")
            mark_list_stale("customers")
            rerun()
        except ApiError as e:
            if "403" in str(e) or "admin" in str(e).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"❌ Erreur: {e}")
