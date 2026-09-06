import streamlit as st
from ..api_client import ApiClient, ApiError
from ..helpers import format_euro, format_kg


def render_kpi_page(client: ApiClient) -> None:
    st.header("📈 Tableau de Bord KPI Stratégique (Directeur & Admin)")
    st.caption(
        "Suivi précis des ventes par produit et lot d'arrivage (Ventes, écoulement de stock, bénéfice net et causes des retours)."
    )

    # Load products for selector
    try:
        products = client.list_products()
    except ApiError as exc:
        st.error(f"Erreur lors du chargement des produits : {exc}")
        return
    except Exception as exc:
        st.error(f"Erreur inattendue : {exc}")
        return

    # Select Product
    product_options = {p["id"]: f"{p['nom']} ({p['categorie']})" for p in products}
    product_options[None] = "Tous les produits"

    col_prod, col_lot = st.columns(2)

    with col_prod:
        selected_product_id = st.selectbox(
            "1. Sélectionner un Produit",
            options=[None] + [p["id"] for p in products],
            format_func=lambda pid: product_options.get(pid, "Tous les produits"),
            key="kpi_select_product",
        )

    # Load lots for the selected product
    try:
        lots = client.get_kpi_lots(selected_product_id)
    except ApiError as exc:
        st.error(f"Erreur lors du chargement des lots d'arrivage : {exc}")
        return

    if not lots:
        st.info("Aucun lot d'arrivage trouvé pour cette sélection.")
        return

    lot_options = {
        l["id"]: f"Arrivée du {l['date_obtenu']} — {l['nom_produit_texte']} ({format_kg(l['kilo_produit'])}, {l['origine']})"
        for l in lots
    }

    with col_lot:
        selected_lot_id = st.selectbox(
            "2. Sélectionner la Date d'arrivée / Lot",
            options=[l["id"] for l in lots],
            format_func=lambda lid: lot_options.get(lid, f"Lot #{lid}"),
            key="kpi_select_lot",
        )

    if not selected_lot_id:
        st.warning("Veuillez sélectionner un lot d'arrivage ci-dessus.")
        return

    # Fetch Analytics for the selected Lot
    try:
        analytics = client.get_kpi_analytics(selected_lot_id)
    except ApiError as exc:
        st.error(f"Erreur lors de la récupération des KPI du lot : {exc}")
        return

    fourniture = analytics.get("fourniture", {})
    kpis = analytics.get("kpis", {})

    st.markdown("---")

    # Header Card for Lot Info
    st.subheader(f"📦 Arrivage : {fourniture.get('nom_produit_texte')}")
    st.markdown(
        f"**Date d'arrivée :** `{fourniture.get('date_obtenu')}` | "
        f"**Fournisseur :** `{fourniture.get('nom_fournisseur')}` ({fourniture.get('origine')}) | "
        f"**Stock Reçu :** `{format_kg(fourniture.get('kilo_produit'))}` | "
        f"**Coût total d'achat :** `{format_euro(fourniture.get('cout_total_achat'))}`"
    )

    st.markdown("### 📊 Indicateurs Clés de Performance (KPI)")

    m1, m2, m3, m4 = st.columns(4)

    # 1. Kilos vendus
    with m1:
        st.metric(
            label="Kilos Vendus",
            value=format_kg(kpis.get("total_kg_vendus")),
            delta=f"{kpis.get('nb_ventes')} vente(s)",
        )

    # 2. Écoulement
    with m2:
        if kpis.get("est_tout_vendu"):
            jours = kpis.get("jours_pour_tout_vendre")
            st.metric(
                label="Écoulement du Stock",
                value=f"{jours} jour(s)",
                delta="Tout est vendu ! 🎉",
                delta_color="normal",
            )
        else:
            st.metric(
                label="Stock Restant (Non vendu)",
                value=format_kg(kpis.get("kilo_restant")),
                delta="Vente en cours",
                delta_color="off",
            )

    # 3. Bénéfice Net
    with m3:
        b_net = kpis.get("benefice_net", 0)
        marge = kpis.get("marge_pct", 0)
        st.metric(
            label="Bénéfice Net Lot",
            value=format_euro(b_net),
            delta=f"Marge {marge}%",
            delta_color="normal" if b_net >= 0 else "inverse",
        )

    # 4. Retours
    with m4:
        ret_kg = kpis.get("total_kg_retours", 0)
        nb_retours = kpis.get("nb_retours", 0)
        st.metric(
            label="Kilos Retournés",
            value=format_kg(ret_kg),
            delta=f"{nb_retours} retour(s)",
            delta_color="inverse" if ret_kg > 0 else "off",
        )

    st.markdown("---")

    # Commandes retournées et causes de retour
    st.subheader("↩️ Commandes Retournées & Causes de Retour")
    retours = kpis.get("commandes_retournees", [])

    if not retours:
        st.success("✅ Aucune commande retournée enregistrée pour cet arrivage.")
    else:
        st.write("Voici la liste des retours clients et leurs motifs :")
        table_data = []
        for r in retours:
            table_data.append(
                {
                    "Date de retour": r.get("date") or "—",
                    "Origine / Client": r.get("origine"),
                    "Quantité (kg)": format_kg(r.get("kilo")),
                    "Cause / Motif du Retour": r.get("cause"),
                }
            )
        st.dataframe(table_data, use_container_width=True)
