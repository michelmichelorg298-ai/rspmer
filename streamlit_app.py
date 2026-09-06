import os
import streamlit as st

from ui.api_client import ApiClient
from ui.session import init_session_state
from ui.components.auth import render_auth_sidebar
from ui.components.products import render_products_page
from ui.components.fournitures import render_fournitures_page
from ui.components.ventes import render_ventes_page
from ui.components.commandes_retour import render_commandes_retour_page
from ui.components.expenses import render_expenses_page
from ui.components.kpi import render_kpi_page

st.set_page_config(
    page_title="FruitMer - Gestion Poissonnerie",
    page_icon="🐟",
    layout="wide",
)

init_session_state()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

client = render_auth_sidebar(API_URL)

st.title("🐟 FruitMer - Gestion Poissonnerie")

if not client:
    st.info("Veuillez vous connecter dans le panneau latéral pour accéder au système de gestion.")
    st.stop()

tab_kpis, tab_products, tab_fournitures, tab_ventes, tab_retours, tab_expenses = st.tabs([
    "📈 Tableau KPI Directeur",
    "📦 Produits / Stock",
    "🚚 Fournitures",
    "💰 Ventes",
    "↩️ Commandes Retour",
    "💸 Dépenses"
])

with tab_kpis:
    render_kpi_page(client)

with tab_products:
    render_products_page(client)

with tab_fournitures:
    render_fournitures_page(client)

with tab_ventes:
    render_ventes_page(client)

with tab_retours:
    render_commandes_retour_page(client)

with tab_expenses:
    render_expenses_page(client)
