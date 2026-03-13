import streamlit as st

st.set_page_config(
    page_title="FII Monitor",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Importa as páginas
from pages_content import cadastro_ativos

# Sidebar de navegação
st.sidebar.title("🏢 FII Monitor")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegação",
    ["📋 Cadastro de Ativos"],
    label_visibility="collapsed",
)

if pagina == "📋 Cadastro de Ativos":
    cadastro_ativos.render()
