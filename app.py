import streamlit as st
from database_setup import setup_database

setup_database(verbose=False)

st.set_page_config(
    page_title="FII Monitor",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Importa as páginas
from pages_content import cadastro_ativos
from pages_content import carteira

# Sidebar de navegação
st.sidebar.title("🏢 FII Monitor")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegação",
    ["📈 Carteira", "📋 Cadastro de Ativos"],
    label_visibility="collapsed",
)

if pagina == "📈 Carteira":
    carteira.render()

if pagina == "📋 Cadastro de Ativos":
    cadastro_ativos.render()
