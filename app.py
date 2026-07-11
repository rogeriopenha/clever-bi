import os
import base64
import streamlit as st

_ROOT = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="CLEVER-BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a Bug': None,
        'About': None
    }
)

if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboards"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "tema" not in st.session_state:
    st.session_state.tema = "clever_dark"

from modules.auth import verificar_login, fazer_logout
from modules.themes import css_tema, get_cores, seletor_tema
from modules.i18n import t, IDIOMAS

# CSS dinâmico do tema
st.markdown(css_tema(), unsafe_allow_html=True)

user = verificar_login()

if user:
    cores = get_cores()

    # --- SIDEBAR ---
    with st.sidebar:
        # Seletor de idioma no topo
        idioma_atual = st.session_state.get("idioma", "pt-br")
        info_atual = IDIOMAS.get(idioma_atual, IDIOMAS["pt-br"])
        sigla_atual = info_atual["sigla"]
        opcoes_lista = list(IDIOMAS.keys())
        idx = next((i for i, k in enumerate(opcoes_lista) if k == idioma_atual), 0)

        st.markdown('<div style="margin-top:-20px">', unsafe_allow_html=True)
        col_f, col_s = st.columns([1, 5])
        with col_f:
            st.markdown(
                f'<img src="https://flagcdn.com/16x12/{sigla_atual}.png" '
                f'style="width:16px;height:12px;margin-top:6px;border-radius:1px">',
                unsafe_allow_html=True
            )
        with col_s:
            escolha = st.selectbox(
                "Idioma",
                options=opcoes_lista,
                format_func=lambda k: IDIOMAS[k]["nome_nativo"],
                index=idx,
                key="lang_sidebar",
                label_visibility="collapsed"
            )
        if escolha and escolha != idioma_atual:
            st.session_state.idioma = escolha
            from modules.database import save_preferences
            save_preferences(idioma=escolha)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Logo + título
        with open(os.path.join(_ROOT, "Logo-CleverBI.svg"), "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode("utf-8")
        _logo_img = f'<img src="data:image/svg+xml;base64,{_b64}" style="height:36px;width:auto">'
        st.markdown(f"""
            <div class="sidebar-header">
                <div class="sidebar-logo">{_logo_img}</div>
                <div>
                    <div class="sidebar-title">CLEVER</div>
                    <div class="sidebar-subtitle">{t('app.subtitulo')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='nav-section-label'>MÓDULOS</div>", unsafe_allow_html=True)

        # Navegação principal com destaque na página ativa
        paginas = [
            ("dashboards", t("nav.dashboards"), "nav_dashboards"),
            ("ia", t("nav.ia"), "nav_ia"),
            ("fontes", t("nav.fontes"), "nav_fontes"),
            ("etl", t("nav.etl"), "nav_etl"),
            ("automacao", t("nav.automacao"), "nav_automacao"),
        ]

        pagina_atual = st.session_state.pagina
        for key, label, btn_key in paginas:
            is_active = pagina_atual == key
            active_class = "nav-item-active" if is_active else ""
            if is_active:
                st.markdown(f'<div class="nav-active-wrapper">', unsafe_allow_html=True)
            if st.button(label, use_container_width=True, key=btn_key):
                st.session_state.pagina = key
                st.rerun()
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div class='nav-section-label'>SISTEMA</div>", unsafe_allow_html=True)

        if st.button(t("nav.config"), use_container_width=True, key="nav_config"):
            st.session_state.pagina = "config"
            st.rerun()

        st.markdown("---")

        # Card do usuário
        cargo = user.get('funcao', 'viewer')
        badge_color = {"admin": "#e63946", "editor": "#4a7cf7", "viewer": "#2ecc71"}.get(cargo, "#6b7fa3")
        st.markdown(f"""
            <div class="user-card">
                <div class="user-avatar" style="background:{cores['accent']}">
                    {user.get('nome', 'U')[:1].upper()}
                </div>
                <div class="user-info">
                    <div class="user-name">{user.get('nome', 'Usuário')}</div>
                    <div class="user-role">
                        <span class="role-badge" style="background:{badge_color}">{cargo}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button(t("nav.sair"), use_container_width=True, key="nav_logout"):
            fazer_logout()

    # --- MAIN CONTENT ---
    pagina = st.session_state.pagina
    from modules.dashboards import tela_dashboards, render_dashboard, editar_dashboard

    # Header da página
    titulos = {
        "dashboards": "📊 " + t("dash.titulo"),
        "ia": "🧠 " + t("ia.titulo"),
        "fontes": "🔌 " + t("fontes.titulo"),
        "etl": "🔄 " + t("nav.etl"),
        "automacao": "🤖 " + t("nav.automacao"),
        "config": "⚙️ " + t("config.titulo"),
    }
    titulo_pagina = titulos.get(pagina, "CLEVER-BI")

    # Mostrar header nas páginas principais (não em subpáginas de dashboard)
    if pagina in titulos:
        st.markdown(f"""
            <div class="page-header">
                <div>
                    <div class="page-title">{titulo_pagina}</div>
                    <div class="page-breadcrumb">
                        <span class="breadcrumb-item">CLEVER</span>
                        <span class="breadcrumb-sep">›</span>
                        <span class="breadcrumb-item breadcrumb-current">{titulo_pagina.split(' ', 1)[-1] if ' ' in titulo_pagina else titulo_pagina}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Roteamento
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
    elif pagina == "etl":
        from modules.etl import tela_etl
        tela_etl()
    elif pagina == "automacao":
        from modules.automacao import tela_automacao
        tela_automacao()
    elif pagina == "fontes":
        from modules.data_sources import gerenciar_fontes
        gerenciar_fontes()
    elif pagina == "config":
        seletor_tema()
        st.markdown("---")
        st.markdown(f"**{t('config.usuario')}:** {user.get('email', '')}")
        st.markdown(f"**{t('config.funcao')}:** {user.get('funcao', '')}")
        if st.session_state.get("tenant_id"):
            st.markdown(f"**Tenant ID:** {st.session_state.tenant_id}")
        st.markdown("---")
        st.caption("CLEVER-BI v0.1 — © 2026")
