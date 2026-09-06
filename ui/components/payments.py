import streamlit as st
import pandas as pd
from datetime import date
from ui.api_client import ApiClient, ApiError
from ui.helpers import get_cached_list, invalidate_cache, mark_list_stale, rerun, safe_index

MODES_PAIEMENT = ["Espèces", "Chèque", "Virement", "Carte"]
TYPES_TIERS = ["FOURNISSEUR", "CLIENT"]


def _format_expense_option(expense: dict) -> str:
    label = expense.get("nomproduit", "?")
    montant = expense.get("prix") or expense.get("montant_restant_du") or 0
    restant = expense.get("montant_restant_du", montant)
    return f"#{expense['id']} — {label} — restant {float(restant):.2f} €"


def _format_sale_option(sale: dict) -> str:
    restant = sale.get("montant_restant_du", 0)
    date_v = sale.get("date_vente", "")
    return f"#{sale['id']} — {date_v} — restant {float(restant):.2f} €"


def render_add_payment(api_client: ApiClient):
    st.subheader("➕ Ajouter un Paiement")

    try:
        expenses = api_client.list_expenses()
        sales = api_client.list_sales()
    except ApiError as e:
        st.error(f"❌ Impossible de charger les dépenses/ventes : {e}")
        return

    unpaid_expenses = [
        e for e in expenses
        if float(e.get("montant_restant_du") or e.get("prix") or 0) > 0.01
    ]
    unpaid_sales = [
        s for s in sales
        if float(s.get("montant_restant_du") or 0) > 0.01
    ]

    with st.form("add_payment_form"):
        col1, col2 = st.columns(2)

        with col1:
            payment_date = st.date_input("Date de paiement", value=date.today())
            montant = st.number_input("Montant (€) *", min_value=0.0, step=0.01)

        with col2:
            type_tiers = st.selectbox("Type *", TYPES_TIERS)
            mode_paiement = st.selectbox("Mode de paiement", MODES_PAIEMENT)

        reference = st.text_input("Référence (numéro chèque, etc.)")
        notes = st.text_area("Notes")

        purchase_id = None
        sale_id = None

        if type_tiers == "FOURNISSEUR":
            if not unpaid_expenses:
                st.warning("Aucune dépense avec solde restant.")
            else:
                expense_labels = [_format_expense_option(e) for e in unpaid_expenses]
                selected = st.selectbox("Dépense à payer *", expense_labels)
                purchase_id = unpaid_expenses[expense_labels.index(selected)]["id"]
        else:
            if not unpaid_sales:
                st.warning("Aucune vente avec solde restant.")
            else:
                sale_labels = [_format_sale_option(s) for s in unpaid_sales]
                selected = st.selectbox("Vente à payer *", sale_labels)
                sale_id = unpaid_sales[sale_labels.index(selected)]["id"]

        if st.form_submit_button("✅ Enregistrer le paiement"):
            if montant <= 0:
                st.error("Le montant doit être > 0")
                return
            if type_tiers == "FOURNISSEUR" and not purchase_id:
                st.error("Sélectionnez une dépense à payer")
                return
            if type_tiers == "CLIENT" and not sale_id:
                st.error("Sélectionnez une vente à payer")
                return

            try:
                payload = {
                    "date_paiement": payment_date.isoformat(),
                    "montant": montant,
                    "type_tiers": type_tiers,
                    "mode_paiement": mode_paiement,
                    "reference": reference if reference.strip() else None,
                    "notes": notes if notes.strip() else None,
                }
                if purchase_id:
                    payload["purchase_id"] = purchase_id
                if sale_id:
                    payload["sale_id"] = sale_id

                result = api_client.create_payment(payload)
                st.success(f"✅ Paiement enregistré avec l'ID {result['id']}")
                mark_list_stale("payments")
                mark_list_stale("sales")
                mark_list_stale("expenses")
                rerun()
            except ApiError as e:
                st.error(f"❌ Erreur: {e}")


def render_payment_list(api_client: ApiClient):
    st.subheader("📋 Liste des Paiements")

    if st.button("🔄 Actualiser", key="refresh_payments"):
        mark_list_stale("payments")

    try:
        payments = get_cached_list("payments", api_client.list_payments)

        if not payments:
            st.info("Aucun paiement trouvé")
            return

        df = pd.DataFrame(payments)
        cols = [
            "id", "date_paiement", "montant", "type_tiers",
            "mode_paiement", "purchase_id", "sale_id", "created_at",
        ]
        display_cols = [c for c in cols if c in df.columns]
        df_display = df[display_cols].copy()
        labels = {
            "id": "ID",
            "date_paiement": "Date paiement",
            "montant": "Montant €",
            "type_tiers": "Type",
            "mode_paiement": "Mode",
            "purchase_id": "Dépense ID",
            "sale_id": "Vente ID",
            "created_at": "Enregistré le",
        }
        df_display.columns = [labels.get(c, c) for c in display_cols]
        if "Date paiement" in df_display.columns:
            df_display["Date paiement"] = pd.to_datetime(df_display["Date paiement"]).dt.strftime("%d/%m/%Y")
        if "Enregistré le" in df_display.columns:
            df_display["Enregistré le"] = pd.to_datetime(df_display["Enregistré le"]).dt.strftime("%d/%m/%Y %H:%M")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as e:
        st.error(f"❌ Erreur: {e}")


def render_edit_payment(api_client: ApiClient):
    st.subheader("✏️ Modifier un Paiement")
    st.caption("Le type et la vente/dépense liée ne sont pas modifiables.")

    payment_id = st.number_input("ID du paiement à modifier", min_value=1, step=1, key="edit_payment_id")

    if st.button("📥 Charger les données", key="load_payment_btn"):
        try:
            st.session_state.current_payment = api_client.get_payment(payment_id)
            st.session_state.current_payment_id = payment_id
        except ApiError as e:
            st.error(f"❌ Erreur: {e}")

    if "current_payment" in st.session_state:
        payment = st.session_state.current_payment
        edit_id = st.session_state.get("current_payment_id", payment_id)

        with st.form("edit_payment_form"):
            col1, col2 = st.columns(2)

            with col1:
                payment_date = st.date_input(
                    "Date de paiement",
                    value=pd.to_datetime(payment["date_paiement"]).date(),
                )
                montant = st.number_input("Montant (€)", value=float(payment["montant"]), step=0.01)

            with col2:
                st.text_input("Type", value=payment.get("type_tiers", ""), disabled=True)
                mode_paiement = st.selectbox(
                    "Mode de paiement",
                    MODES_PAIEMENT,
                    index=safe_index(MODES_PAIEMENT, payment.get("mode_paiement"), 0),
                )

            reference = st.text_input("Référence", value=payment.get("reference") or "")
            notes = st.text_area("Notes", value=payment.get("notes") or "")

            if st.form_submit_button("✅ Mettre à jour"):
                try:
                    payload = {
                        "date_paiement": payment_date.isoformat(),
                        "montant": montant,
                        "mode_paiement": mode_paiement,
                        "reference": reference if reference.strip() else None,
                        "notes": notes if notes.strip() else None,
                    }
                    api_client.update_payment(edit_id, payload)
                    st.success("✅ Paiement mis à jour")
                    invalidate_cache("current_payment", "current_payment_id")
                    mark_list_stale("payments")
                    mark_list_stale("sales")
                    mark_list_stale("expenses")
                    rerun()
                except ApiError as e:
                    st.error(f"❌ Erreur: {e}")


def render_delete_payment(api_client: ApiClient):
    st.subheader("🗑️ Supprimer un Paiement")
    st.caption("Rôle administrateur requis.")

    payment_id = st.number_input("ID du paiement à supprimer", min_value=1, step=1, key="delete_payment_id")

    if st.button("🗑️ Supprimer", key="btn_delete_payment"):
        try:
            api_client.delete_payment(payment_id)
            st.success("✅ Paiement supprimé")
            mark_list_stale("payments")
            mark_list_stale("sales")
            mark_list_stale("expenses")
            rerun()
        except ApiError as e:
            if "403" in str(e) or "admin" in str(e).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"❌ Erreur: {e}")
