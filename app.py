import streamlit as st

st.set_page_config(
    page_title="CLEVER-BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboards"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "tema" not in st.session_state:
    st.session_state.tema = "clever_dark"

from modules.auth import verificar_login, fazer_logout
from modules.themes import css_tema, get_cores, seletor_tema

# CSS dinâmico do tema
st.markdown(css_tema(), unsafe_allow_html=True)

user = verificar_login()

if user:
    cores = get_cores()

    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:1rem 0">
                <h1 style="color:{cores['text_primary']};font-size:1.8rem;margin:0">CLEVER</h1>
                <p style="color:{cores['accent']};font-size:0.8rem;margin:0">Business Intelligence</p>
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
            <div style="padding:0.5rem;background:{cores['bg_secondary']};border-radius:8px;text-align:center;border:1px solid {cores['border']}">
                <p style="color:{cores['text_primary']};font-size:0.85rem;margin:0">{user.get('nome', 'Usuário')}</p>
                <p style="color:{cores['text_secondary']};font-size:0.7rem;margin:0">{user.get('funcao', 'viewer')}</p>
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
        st.markdown(f"""
            <h1 style="color:{cores['text_primary']}">⚙️ Configurações</h1>
            <p style="color:{cores['text_secondary']}">Configurações do sistema</p>
        """, unsafe_allow_html=True)

        seletor_tema()

        st.markdown("---")
        st.markdown(f"**Usuário:** {user.get('email', '')}")
        st.markdown(f"**Função:** {user.get('funcao', '')}")
        if st.session_state.get("tenant_id"):
            st.markdown(f"**Tenant ID:** {st.session_state.tenant_id}")
        st.markdown("---")
        st.caption("CLEVER-BI v0.1 — © 2026")
