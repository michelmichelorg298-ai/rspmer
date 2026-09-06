import streamlit as st
import pandas as pd
from datetime import date
from ui.api_client import ApiClient, ApiError
from ui.helpers import get_cached_list, invalidate_cache, mark_list_stale, rerun, safe_index

STATUTS = ["Non payé", "Partiellement payé", "Payé"]


def _load_customers_products(api_client: ApiClient):
    customers = api_client.list_customers()
    products = api_client.list_products()
    customer_dict = {c["nom"]: c["id"] for c in customers}
    product_dict = {p["nom"]: p["id"] for p in products}
    return customers, customer_dict, list(customer_dict.keys()), product_dict, list(product_dict.keys())


def render_add_sale(api_client: ApiClient):
    st.subheader("➕ Créer une Vente")

    try:
        customers, customer_dict, customer_list, product_dict, product_list = _load_customers_products(api_client)
    except ApiError:
        st.error("❌ Impossible de charger les clients/produits")
        return

    if not customer_list:
        st.warning("⚠️ Aucun client trouvé. Créez d'abord un client.")
        return

    if not product_list:
        st.warning("⚠️ Aucun produit trouvé. Créez d'abord un produit.")
        return

    if "num_sale_items" not in st.session_state:
        st.session_state.num_sale_items = 1

    with st.form("add_sale_form"):
        col1, col2 = st.columns(2)

        with col1:
            sale_date = st.date_input("Date de la vente", value=date.today())
            customer_name = st.selectbox("Client *", customer_list)

        with col2:
            st.info("Le statut de paiement est calculé automatiquement à la création (Non payé).")

        notes = st.text_area("Notes")

        st.divider()
        st.write("**📦 Articles de la vente (minimum 1 article)**")

        sale_items = []
        for i in range(st.session_state.num_sale_items):
            col_product, col_qty, col_price = st.columns(3)
            with col_product:
                product_name = st.selectbox(
                    "Produit",
                    product_list,
                    key=f"sale_product_{i}",
                    label_visibility="collapsed",
                )
            with col_qty:
                qty = st.number_input(
                    "Kg",
                    min_value=0.1,
                    step=0.1,
                    key=f"sale_qty_{i}",
                    label_visibility="collapsed",
                )
            with col_price:
                price = st.number_input(
                    "Prix/kg",
                    min_value=0.0,
                    step=1.0,
                    key=f"sale_price_{i}",
                    label_visibility="collapsed",
                )

            if product_name and qty > 0 and price >= 0:
                sale_items.append({
                    "product_id": product_dict[product_name],
                    "kilo_vendu": qty,
                    "prix_unitaire_kg": price,
                })

        if st.form_submit_button("✅ Créer la vente"):
            if not customer_name:
                st.error("Veuillez sélectionner un client")
                return
            if not sale_items:
                st.error("Ajoutez au moins 1 article valide (produit, kg > 0, prix ≥ 0)")
                return

            montant_total = sum(item["kilo_vendu"] * item["prix_unitaire_kg"] for item in sale_items)

            try:
                payload = {
                    "date_vente": sale_date.isoformat(),
                    "customer_id": customer_dict[customer_name],
                    "notes": notes if notes.strip() else None,
                    "items": sale_items,
                }
                result = api_client.create_sale(payload)
                st.success(
                    f"✅ Vente créée (ID {result['id']}) — "
                    f"Montant: {result.get('montant_total_ttc', montant_total):.2f} €"
                )
                st.session_state.num_sale_items = 1
                mark_list_stale("sales")
                mark_list_stale("products")
                rerun()
            except ApiError as e:
                st.error(f"❌ Erreur: {e}")

    st.divider()
    col_add, col_remove = st.columns(2)
    with col_add:
        if st.button("➕ Ajouter une ligne", key="add_sale_item_btn"):
            st.session_state.num_sale_items += 1
            rerun()
    with col_remove:
        if st.button("➖ Supprimer dernière ligne", key="remove_sale_item_btn"):
            if st.session_state.num_sale_items > 1:
                st.session_state.num_sale_items -= 1
                rerun()


def render_sale_list(api_client: ApiClient):
    st.subheader("📋 Liste des Ventes")

    if st.button("🔄 Actualiser", key="refresh_sales"):
        mark_list_stale("sales")

    try:
        sales = get_cached_list("sales", api_client.list_sales)

        if not sales:
            st.info("Aucune vente trouvée")
            return

        df = pd.DataFrame(sales)
        cols = ["id", "date_vente", "customer_id", "montant_total_ttc", "statut", "montant_restant_du"]
        display_cols = [c for c in cols if c in df.columns]
        df_display = df[display_cols].copy()
        labels = {
            "id": "ID",
            "date_vente": "Date vente",
            "customer_id": "Client ID",
            "montant_total_ttc": "Montant TTC €",
            "statut": "Statut",
            "montant_restant_du": "Restant dû €",
        }
        df_display.columns = [labels.get(c, c) for c in display_cols]
        if "Date vente" in df_display.columns:
            df_display["Date vente"] = pd.to_datetime(df_display["Date vente"]).dt.strftime("%d/%m/%Y")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except ApiError as e:
        st.error(f"❌ Erreur: {e}")


def render_edit_sale(api_client: ApiClient):
    st.subheader("✏️ Modifier une Vente")
    st.caption("Seuls la date, le client, les notes et l'échéance sont modifiables via l'API.")

    sale_id = st.number_input("ID de la vente à modifier", min_value=1, step=1, key="edit_sale_id")

    if st.button("📥 Charger les données", key="load_sale_btn"):
        try:
            st.session_state.current_sale = api_client.get_sale(sale_id)
            st.session_state.current_sale_id = sale_id
        except ApiError as e:
            st.error(f"❌ Erreur: {e}")

    if "current_sale" in st.session_state:
        sale = st.session_state.current_sale
        edit_id = st.session_state.get("current_sale_id", sale_id)

        try:
            customers, customer_dict, customer_list, _, _ = _load_customers_products(api_client)
        except ApiError:
            st.error("❌ Impossible de charger les clients")
            return

        current_customer = next((c for c in customers if c["id"] == sale.get("customer_id")), None)
        current_customer_name = current_customer["nom"] if current_customer else customer_list[0]

        with st.form("edit_sale_form"):
            col1, col2 = st.columns(2)

            with col1:
                sale_date = st.date_input(
                    "Date de la vente",
                    value=pd.to_datetime(sale["date_vente"]).date(),
                )
                customer_name = st.selectbox(
                    "Client",
                    customer_list,
                    index=safe_index(customer_list, current_customer_name, 0),
                )

            with col2:
                st.metric("Montant TTC (€)", f"{sale.get('montant_total_ttc', 0):.2f}")
                st.metric("Statut", sale.get("statut", "—"))
                st.metric("Restant dû (€)", f"{sale.get('montant_restant_du', 0):.2f}")

            notes = st.text_area("Notes", value=sale.get("notes") or "")

            if st.form_submit_button("✅ Mettre à jour"):
                try:
                    payload = {
                        "date_vente": sale_date.isoformat(),
                        "customer_id": customer_dict[customer_name],
                        "notes": notes if notes.strip() else None,
                    }
                    api_client.update_sale(edit_id, payload)
                    st.success("✅ Vente mise à jour")
                    invalidate_cache("current_sale", "current_sale_id")
                    mark_list_stale("sales")
                    rerun()
                except ApiError as e:
                    st.error(f"❌ Erreur: {e}")


def render_delete_sale(api_client: ApiClient):
    st.subheader("🗑️ Supprimer une Vente")
    st.caption("Rôle administrateur requis.")

    sale_id = st.number_input("ID de la vente à supprimer", min_value=1, step=1, key="delete_sale_id")

    if st.button("🗑️ Supprimer", key="btn_delete_sale"):
        try:
            api_client.delete_sale(sale_id)
            st.success("✅ Vente supprimée")
            mark_list_stale("sales")
            mark_list_stale("products")
            rerun()
        except ApiError as e:
            if "403" in str(e) or "admin" in str(e).lower():
                st.error("❌ Suppression réservée au compte admin@gmail.com")
            else:
                st.error(f"❌ Erreur: {e}")
