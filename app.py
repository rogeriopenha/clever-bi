import streamlit as st

st.set_page_config(
    page_title="CLEVER-BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1629; }
    .stSidebar { background-color: #1a2340; }
    h1, h2, h3, h4, h5, h6 { color: #e8edf5 !important; }
    p, li, span, div { color: #e8edf5; }
    .st-bw { background-color: #1a2340; }
    .stButton button {
        background-color: #4a7cf7;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton button:hover { background-color: #5a8cf7; }
    .stTextInput input {
        background-color: #1a2340;
        color: #e8edf5;
        border: 1px solid #2a3450;
        border-radius: 8px;
    }
    .stTextArea textarea {
        background-color: #1a2340;
        color: #e8edf5;
        border: 1px solid #2a3450;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1a2340;
        border: 1px solid #2a3450;
        border-radius: 8px;
    }
    .st-emotion-cache-1wrc2r6 { color: #8899b8; }
    div[data-testid="stMetricLabel"] { color: #8899b8; }
    div[data-testid="stMetricValue"] { color: #e8edf5; font-weight: 700; }
    div[data-testid="stMetricDelta"] { color: #4a7cf7; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a2340;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        color: #8899b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4a7cf7;
        color: white !important;
    }
    div.stDataFrame { border: 1px solid #2a3450; border-radius: 8px; }
    section[data-testid="stSidebar"] .st-emotion-cache-1wmy9hl { color: #8899b8; }
</style>
""", unsafe_allow_html=True)

if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboards"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

from modules.auth import verificar_login, fazer_logout

user = verificar_login()

if user:
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:1rem 0">
                <h1 style="color:#e8edf5;font-size:1.8rem;margin:0">CLEVER</h1>
                <p style="color:#4a7cf7;font-size:0.8rem;margin:0">Business Intelligence</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("📊 Dashboards", use_container_width=True, key="nav_dashboards"):
            st.session_state.pagina = "dashboards"
            st.rerun()
        if st.button("🧠 IA", use_container_width=True, key="nav_ia"):
            st.session_state.pagina = "ia"
            st.rerun()
        if st.button("🔌 Fontes de Dados", use_container_width=True, key="nav_fontes"):
            st.session_state.pagina = "fontes"
            st.rerun()
        if st.button("⚙️ Configurações", use_container_width=True, key="nav_config"):
            st.session_state.pagina = "config"
            st.rerun()

        st.markdown("---")

        st.markdown(f"""
            <div style="padding:0.5rem;background:#1a2340;border-radius:8px;text-align:center">
                <p style="color:#e8edf5;font-size:0.85rem;margin:0">{user.get('nome', 'Usuário')}</p>
                <p style="color:#6b7fa3;font-size:0.7rem;margin:0">{user.get('funcao', 'viewer')}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sair", use_container_width=True):
            fazer_logout()

    pagina = st.session_state.pagina

    from modules.dashboards import tela_dashboards, render_dashboard, editar_dashboard

    if pagina == "dashboards":
        tela_dashboards()
    elif pagina == "dashboard_view":
        dash_id = st.session_state.get("dashboard_ativo")
        if dash_id:
            if st.button("← Voltar", key="back_view"):
                st.session_state.pagina = "dashboards"
                st.rerun()
            render_dashboard(dash_id)
    elif pagina == "dashboard_edit":
        dash_id = st.session_state.get("dashboard_ativo")
        if dash_id:
            if st.button("← Voltar", key="back_edit"):
                st.session_state.pagina = "dashboards"
                st.rerun()
            editar_dashboard(dash_id)
    elif pagina == "ia":
        from modules.ai_chat import chat_ia_screen
        chat_ia_screen()
    elif pagina == "fontes":
        from modules.data_sources import gerenciar_fontes
        gerenciar_fontes()
    elif pagina == "config":
        st.markdown("""
            <h1 style="color:#e8edf5">⚙️ Configurações</h1>
            <p style="color:#6b7fa3">Configurações do sistema</p>
        """, unsafe_allow_html=True)
        st.markdown(f"**Usuário:** {user.get('email', '')}")
        st.markdown(f"**Função:** {user.get('funcao', '')}")
        if st.session_state.get("tenant_id"):
            st.markdown(f"**Tenant ID:** {st.session_state.tenant_id}")
        st.markdown("---")
        st.caption("CLEVER-BI v0.1 — © 2026")
