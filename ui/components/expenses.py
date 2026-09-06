from datetime import datetime

import pandas as pd
import streamlit as st

from ui.api_client import ApiClient, ApiError
from ui.helpers import get_cached_list, invalidate_cache, mark_list_stale, rerun

PRODUIT_PREDEFINIS = [
    "Filet de calmar",
    "Tête de poisson",
    "Filet de poisson",
    "Chair de crabe",
    "Poulpe",
    "Gambas",
]
AUTRE_LABEL = "➕ Autre..."
STATUTS_PAIEMENT = ["Payé", "Non payé", "Avance"]


def _produit_selector(
    default_value: str | None = None,
    key_prefix: str = "produit",
) -> str | None:
    options = PRODUIT_PREDEFINIS + [AUTRE_LABEL]
    default_value = (default_value or "").strip()

    if default_value and default_value in PRODUIT_PREDEFINIS:
        index_initial = options.index(default_value)
    else:
        index_initial = len(options) - 1

    choix = st.selectbox(
        "Nom des produits",
        options,
        index=index_initial,
        key=f"{key_prefix}_select",
    )

    if choix == AUTRE_LABEL:
        valeur_autre = st.text_input(
            "Précisez le produit",
            value=default_value if default_value and default_value not in PRODUIT_PREDEFINIS else "",
            key=f"{key_prefix}_autre",
            placeholder="Ex: Crevettes, Homard...",
        )
        return valeur_autre.strip() or None
    return choix


def render_add_expense(client: ApiClient) -> None:
    st.subheader("➕ Ajouter une dépense")

    with st.form("add_depense_form"):
        col1, col2 = st.columns(2)
        with col1:
            joudate = st.date_input("Date de la dépense", key="add_joudate")
            nomproduit = _produit_selector(key_prefix="add")
            kilo = st.number_input(
                "Kilogrammes / Quantité",
                min_value=0.0,
                step=0.1,
                value=0.0,
                key="add_kilo",
            )
        with col2:
            prix = st.number_input(
                "Prix total",
                min_value=0.0,
                step=0.5,
                value=0.0,
                key="add_prix",
            )
            paye = st.selectbox(
                "Statut de paiement",
                STATUTS_PAIEMENT,
                key="add_paye",
            )
            nompersonnepret = st.text_input(
                "Prêté à (optionnel)",
                key="add_nompersonnepret",
            )

        submit = st.form_submit_button("Enregistrer la dépense", key="add_submit")

        if submit:
            if not nomproduit:
                st.error("Le nom du produit est obligatoire.")
            else:
                data = {
                    "joudate": joudate.isoformat(),
                    "kilo": kilo,
                    "prix": prix,
                    "paye": paye,
                    "nomproduit": nomproduit,
                    "nompersonnepret": nompersonnepret if nompersonnepret else None,
                }
                try:
                    client.create_expense(data)
                    st.success("Dépense enregistrée avec succès !")
                    mark_list_stale("expenses")
                    rerun()
                except ApiError as exc:
                    st.error(f"Erreur API : {exc}")


def render_expense_list(client: ApiClient) -> None:
    st.subheader("📋 Liste des dépenses")

    if st.button("🔄 Actualiser", key="refresh_expenses"):
        mark_list_stale("expenses")

    try:
        depences = get_cached_list("expenses", client.list_expenses)

        if not depences:
            st.info("Aucune dépense enregistrée pour le moment.")
            return

        df = pd.DataFrame(depences)
        desired_cols = [
            "id",
            "joudate",
            "nomproduit",
            "kilo",
            "prix",
            "paye",
            "montant_restant_du",
            "nompersonnepret",
        ]
        display_cols = [c for c in desired_cols if c in df.columns]
        labels = {
            "id": "ID",
            "joudate": "Date",
            "nomproduit": "Produit",
            "kilo": "Kg",
            "prix": "Prix €",
            "paye": "Statut",
            "montant_restant_du": "Restant dû €",
            "nompersonnepret": "Prêté à",
        }
        df_display = df[display_cols].copy()
        df_display.columns = [labels.get(c, c) for c in display_cols]
        if "Date" in df_display.columns:
            df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.strftime("%d/%m/%Y")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as exc:
        st.error(f"Erreur de connexion : {exc}")


def render_edit_expense(client: ApiClient) -> None:
    st.subheader("✏️ Modifier une dépense")

    expense_id = st.number_input(
        "ID de la dépense à modifier",
        min_value=1,
        step=1,
        key="update_id_input",
    )

    if st.button("📥 Charger les données", key="load_data_btn"):
        try:
            st.session_state.update_data = client.get_expense(expense_id)
            st.session_state.update_expense_id = expense_id
        except ApiError as exc:
            st.error(f"Dépense ID {expense_id} introuvable : {exc}")

    if "update_data" in st.session_state:
        data = st.session_state.update_data
        edit_id = st.session_state.get("update_expense_id", expense_id)
        d_kilo = float(data.get("kilo", 0) or 0)
        d_prix = float(data.get("prix", 0) or 0)
        d_date = datetime.now().date()
        try:
            if data.get("joudate"):
                d_date = pd.to_datetime(data["joudate"]).date()
        except Exception:
            pass

        with st.form("edit_form"):
            u_date = st.date_input("Date", value=d_date, key="edit_joudate")
            u_produit = _produit_selector(
                default_value=data.get("nomproduit", ""),
                key_prefix="edit",
            )
            u_kilo = st.number_input("Kilo", value=d_kilo, key="edit_kilo")
            u_prix = st.number_input("Prix", value=d_prix, key="edit_prix")
            u_paye = st.selectbox(
                "Statut paiement",
                STATUTS_PAIEMENT,
                index=STATUTS_PAIEMENT.index(data.get("paye"))
                if data.get("paye") in STATUTS_PAIEMENT
                else 1,
                key="edit_paye",
            )
            u_pret = st.text_input(
                "Prêté à",
                value=data.get("nompersonnepret", "") or "",
                key="edit_nompersonnepret",
            )

            if st.form_submit_button("Appliquer les modifications", key="edit_submit"):
                if not u_produit:
                    st.error("Le nom du produit est obligatoire.")
                else:
                    update_payload = {
                        "joudate": u_date.isoformat(),
                        "kilo": u_kilo,
                        "prix": u_prix,
                        "paye": u_paye,
                        "nomproduit": u_produit,
                        "nompersonnepret": u_pret if u_pret else None,
                    }
                    try:
                        client.update_expense(edit_id, update_payload)
                        st.success("Modification réussie !")
                        invalidate_cache("update_data", "update_expense_id")
                        mark_list_stale("expenses")
                        rerun()
                    except ApiError as exc:
                        st.error(f"Erreur modification : {exc}")


def render_delete_expense(client: ApiClient) -> None:
    st.subheader("🗑️ Supprimer une dépense")
    st.caption("Rôle administrateur requis.")

    col_del1, col_del2 = st.columns([3, 1])
    with col_del1:
        expense_id = st.number_input(
            "ID à supprimer",
            min_value=1,
            step=1,
            key="delete_id_input",
        )
    with col_del2:
        st.write("##")
        del_btn = st.button("Supprimer", use_container_width=True, key="delete_btn")

    if del_btn:
        try:
            client.delete_expense(expense_id)
            st.success(f"Dépense {expense_id} supprimée.")
            mark_list_stale("expenses")
            rerun()
        except ApiError as exc:
            if "403" in str(exc) or "admin" in str(exc).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"Erreur : {exc}")
