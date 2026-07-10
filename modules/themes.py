import streamlit as st
import json
from modules.i18n import t, token_label

TEMAS_PADRAO = {
    "clever_dark": {
        "nome": "CLEVER Dark", "icone": "🌙",
        "bg_primary": "#0b1120", "bg_secondary": "#111827",
        "text_primary": "#e2e8f0", "text_secondary": "#64748b",
        "accent": "#3b82f6", "accent_hover": "#60a5fa",
        "border": "#1e293b",
        "metric_label": "#94a3b8", "metric_value": "#f1f5f9", "metric_delta": "#3b82f6",
        "card_bg": "#1a2332", "card_border": "#2d3a4e",
        "tab_inactive_bg": "#1a2332", "tab_inactive_color": "#94a3b8", "tab_active_bg": "#3b82f6",
    },
    "clever_light": {
        "nome": "CLEVER Light", "icone": "☀️",
        "bg_primary": "#f0f4f8", "bg_secondary": "#ffffff",
        "text_primary": "#1e293b", "text_secondary": "#64748b",
        "accent": "#2563eb", "accent_hover": "#3b82f6",
        "border": "#d1d9e6",
        "metric_label": "#64748b", "metric_value": "#1e293b", "metric_delta": "#2563eb",
        "card_bg": "#ffffff", "card_border": "#d1d9e6",
        "tab_inactive_bg": "#e8edf5", "tab_inactive_color": "#64748b", "tab_active_bg": "#2563eb",
    },
    "midnight": {
        "nome": "Midnight", "icone": "🌌",
        "bg_primary": "#07071a", "bg_secondary": "#0d0d2b",
        "text_primary": "#dadaff", "text_secondary": "#7a7abb",
        "accent": "#7c4dff", "accent_hover": "#9c6dff",
        "border": "#1f1f4a",
        "metric_label": "#7a7abb", "metric_value": "#dadaff", "metric_delta": "#7c4dff",
        "card_bg": "#12123a", "card_border": "#24245a",
        "tab_inactive_bg": "#12123a", "tab_inactive_color": "#7a7abb", "tab_active_bg": "#7c4dff",
    },
    "forest": {
        "nome": "Forest", "icone": "🌿",
        "bg_primary": "#0a140e", "bg_secondary": "#112216",
        "text_primary": "#d4edda", "text_secondary": "#6c9a7a",
        "accent": "#22c55e", "accent_hover": "#4ade80",
        "border": "#1e3a24",
        "metric_label": "#6c9a7a", "metric_value": "#d4edda", "metric_delta": "#22c55e",
        "card_bg": "#162920", "card_border": "#244030",
        "tab_inactive_bg": "#162920", "tab_inactive_color": "#6c9a7a", "tab_active_bg": "#22c55e",
    },
    "sunset": {
        "nome": "Sunset", "icone": "🌅",
        "bg_primary": "#1a0e08", "bg_secondary": "#2a1810",
        "text_primary": "#f5e0d0", "text_secondary": "#b08070",
        "accent": "#e67e22", "accent_hover": "#f09a4a",
        "border": "#3a2820",
        "metric_label": "#b08070", "metric_value": "#f5e0d0", "metric_delta": "#e67e22",
        "card_bg": "#2a1810", "card_border": "#3a2820",
        "tab_inactive_bg": "#2a1810", "tab_inactive_color": "#b08070", "tab_active_bg": "#e67e22",
    },
    "ocean": {
        "nome": "Ocean", "icone": "🌊",
        "bg_primary": "#071520", "bg_secondary": "#0c2035",
        "text_primary": "#cce8ff", "text_secondary": "#6a9ec8",
        "accent": "#06b6d4", "accent_hover": "#22d3ee",
        "border": "#143050",
        "metric_label": "#6a9ec8", "metric_value": "#cce8ff", "metric_delta": "#06b6d4",
        "card_bg": "#102840", "card_border": "#1c4060",
        "tab_inactive_bg": "#102840", "tab_inactive_color": "#6a9ec8", "tab_active_bg": "#06b6d4",
    },
    "cherry": {
        "nome": "Cherry", "icone": "🍒",
        "bg_primary": "#1a080c", "bg_secondary": "#2a1018",
        "text_primary": "#f5d4d4", "text_secondary": "#b0707a",
        "accent": "#e63946", "accent_hover": "#f04a58",
        "border": "#3a1a22",
        "metric_label": "#b0707a", "metric_value": "#f5d4d4", "metric_delta": "#e63946",
        "card_bg": "#2a1018", "card_border": "#3a1a22",
        "tab_inactive_bg": "#2a1018", "tab_inactive_color": "#b0707a", "tab_active_bg": "#e63946",
    },
    "gold": {
        "nome": "Gold", "icone": "⭐",
        "bg_primary": "#1a1508", "bg_secondary": "#2a2010",
        "text_primary": "#f5e8c8", "text_secondary": "#b09850",
        "accent": "#f0c040", "accent_hover": "#f8d050",
        "border": "#3a3018",
        "metric_label": "#b09850", "metric_value": "#f5e8c8", "metric_delta": "#f0c040",
        "card_bg": "#2a2010", "card_border": "#3a3018",
        "tab_inactive_bg": "#2a2010", "tab_inactive_color": "#b09850", "tab_active_bg": "#f0c040",
    },
    "dracula": {
        "nome": "Dracula", "icone": "🧛",
        "bg_primary": "#1a1128", "bg_secondary": "#281a36",
        "text_primary": "#f0e0f8", "text_secondary": "#a080b8",
        "accent": "#bd93f9", "accent_hover": "#cfa3ff",
        "border": "#3a2850",
        "metric_label": "#a080b8", "metric_value": "#f0e0f8", "metric_delta": "#bd93f9",
        "card_bg": "#281a36", "card_border": "#3a2850",
        "tab_inactive_bg": "#281a36", "tab_inactive_color": "#a080b8", "tab_active_bg": "#bd93f9",
    },
    "corporate": {
        "nome": "Corporate", "icone": "🏢",
        "bg_primary": "#eef1f5", "bg_secondary": "#ffffff",
        "text_primary": "#1e2a3a", "text_secondary": "#5a7a9a",
        "accent": "#1a6bc4", "accent_hover": "#2a7bd4",
        "border": "#c0c8d4",
        "metric_label": "#5a7a9a", "metric_value": "#1e2a3a", "metric_delta": "#1a6bc4",
        "card_bg": "#ffffff", "card_border": "#c0c8d4",
        "tab_inactive_bg": "#e0e4ea", "tab_inactive_color": "#5a7a9a", "tab_active_bg": "#1a6bc4",
    },
}

TEMA_PADRAO = "clever_dark"
CHAVE_CUSTOM = "temas_customizados"

def obter_todos_temas() -> dict:
    temas = dict(TEMAS_PADRAO)
    custom = st.session_state.get(CHAVE_CUSTOM, {})
    temas.update(custom)
    return temas

def get_tema() -> str:
    tema = st.session_state.get("tema", TEMA_PADRAO)
    if tema not in obter_todos_temas():
        tema = TEMA_PADRAO
    return tema

def get_cores() -> dict:
    return obter_todos_temas()[get_tema()]

def css_tema() -> str:
    c = get_cores()
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
        html {{ font-size: 15px; }}

        .stApp {{
            background-color: {c["bg_primary"]};
        }}

        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: {c["border"]};
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: {c["text_secondary"]}; }}

        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] > div:first-child {{
            padding: 0 !important;
            margin: 0 !important;
            background: {c["bg_secondary"]};
            border-right: 1px solid {c["border"]};
        }}
        section[data-testid="stSidebar"] > div:nth-child(2) {{
            padding: 1rem 1rem 1rem 1rem !important;
        }}

        .sidebar-header {{
            display: flex; align-items: center; gap: 0.75rem;
            padding: 0.75rem 0 0.5rem 0;
            margin-bottom: 0.5rem;
        }}
        .sidebar-logo {{
            font-size: 2rem; line-height: 1;
            background: linear-gradient(135deg, {c["accent"]}, {c["accent_hover"]});
            width: 44px; height: 44px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }}
        .sidebar-title {{
            font-size: 1.35rem; font-weight: 700; color: {c["text_primary"]};
            letter-spacing: -0.02em; line-height: 1.2;
        }}
        .sidebar-subtitle {{
            font-size: 0.7rem; color: {c["accent"]};
            font-weight: 500; letter-spacing: 0.02em;
            text-transform: uppercase;
        }}

        .nav-section-label {{
            font-size: 0.6rem; font-weight: 600; color: {c["text_secondary"]};
            text-transform: uppercase; letter-spacing: 0.08em;
            margin: 1rem 0 0.25rem 0; padding: 0;
        }}

        /* ===== BOTÕES DE NAVEGAÇÃO ===== */
        section[data-testid="stSidebar"] .stButton button {{
            background: transparent !important;
            color: {c["text_secondary"]} !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 0.75rem !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            text-align: left !important;
            transition: all 0.15s ease !important;
            width: 100% !important;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background: color-mix(in srgb, {c["text_primary"]} 8%, transparent) !important;
            color: {c["text_primary"]} !important;
        }}

        .nav-active-wrapper button {{
            background: color-mix(in srgb, {c["accent"]} 15%, transparent) !important;
            color: {c["accent"]} !important;
            font-weight: 600 !important;
            border-left: 3px solid {c["accent"]} !important;
            border-radius: 8px !important;
            position: relative;
        }}
        .nav-active-wrapper button:hover {{
            background: color-mix(in srgb, {c["accent"]} 25%, transparent) !important;
            color: {c["accent"]} !important;
        }}

        /* ===== USER CARD ===== */
        .user-card {{
            display: flex; align-items: center; gap: 0.65rem;
            padding: 0.65rem; border-radius: 10px;
            background: color-mix(in srgb, {c["text_primary"]} 4%, transparent);
            margin: 0.25rem 0 0.5rem 0;
            transition: background 0.2s;
        }}
        .user-card:hover {{
            background: color-mix(in srgb, {c["text_primary"]} 8%, transparent);
        }}
        .user-avatar {{
            width: 36px; height: 36px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1rem; font-weight: 700; color: white;
            flex-shrink: 0;
        }}
        .user-info {{ flex: 1; min-width: 0; }}
        .user-name {{ font-size: 0.82rem; font-weight: 600; color: {c["text_primary"]}; }}
        .user-role {{ margin-top: 2px; }}
        .role-badge {{
            font-size: 0.6rem; font-weight: 600; text-transform: uppercase;
            padding: 1px 7px; border-radius: 4px; color: white;
            letter-spacing: 0.04em;
        }}

        /* ===== PAGE HEADER ===== */
        .page-header {{
            display: flex; align-items: flex-start; justify-content: space-between;
            margin-bottom: 1.5rem; padding-bottom: 1rem;
            border-bottom: 1px solid {c["border"]};
        }}
        .page-title {{
            font-size: 1.5rem; font-weight: 700; color: {c["text_primary"]};
            letter-spacing: -0.02em;
        }}
        .page-breadcrumb {{
            display: flex; align-items: center; gap: 0.35rem;
            margin-top: 0.15rem; font-size: 0.75rem; color: {c["text_secondary"]};
        }}
        .breadcrumb-item {{ color: {c["text_secondary"]}; }}
        .breadcrumb-sep {{ color: {c["border"]}; font-weight: 300; }}
        .breadcrumb-current {{ color: {c["accent"]}; font-weight: 500; }}

        /* ===== BOTÕES GLOBAIS ===== */
        .stButton button {{
            background: {c["accent"]};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            padding: 0.4rem 1rem;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stButton button:hover {{
            background: {c["accent_hover"]};
            box-shadow: 0 4px 12px color-mix(in srgb, {c["accent"]} 40%, transparent);
            transform: translateY(-1px);
        }}
        .stButton button:active {{
            transform: translateY(0);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stButton button[kind="secondary"] {{
            background: transparent;
            color: {c["accent"]};
            border: 1px solid {c["accent"]};
        }}
        .stButton button[kind="secondary"]:hover {{
            background: color-mix(in srgb, {c["accent"]} 10%, transparent);
        }}

        /* ===== INPUTS ===== */
        .stTextInput input, .stTextArea textarea,
        .stNumberInput input, .stDateInput input, .stTimeInput input {{
            background: {c["bg_secondary"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
            border-radius: 8px;
            transition: border-color 0.2s, box-shadow 0.2s;
            font-size: 0.85rem;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus,
        .stNumberInput input:focus {{
            border-color: {c["accent"]};
            box-shadow: 0 0 0 3px color-mix(in srgb, {c["accent"]} 20%, transparent);
        }}

        /* ===== SELECTBOX ===== */
        .stSelectbox div[data-baseweb="select"],
        .stSelectbox div[data-baseweb="select"] > div {{
            background: {c["bg_secondary"]} !important;
            color: {c["text_primary"]} !important;
            border: 1px solid {c["border"]};
            border-radius: 8px;
            transition: border-color 0.2s;
        }}
        .stSelectbox div[data-baseweb="select"]:focus-within {{
            border-color: {c["accent"]};
            box-shadow: 0 0 0 3px color-mix(in srgb, {c["accent"]} 20%, transparent);
        }}
        .stSelectbox div[data-baseweb="select"] span {{ color: {c["text_primary"]} !important; }}
        .stSelectbox li[role="option"] {{
            background: {c["bg_secondary"]} !important;
            color: {c["text_primary"]} !important;
        }}
        .stSelectbox li[role="option"]:hover {{
            background: {c["accent"]} !important;
            color: white !important;
        }}

        /* ===== MULTISELECT ===== */
        .stMultiSelect div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"] span {{
            background: {c["bg_secondary"]} !important;
            color: {c["text_primary"]} !important;
        }}

        /* ===== METRICAS ===== */
        div[data-testid="stMetricLabel"] {{
            color: {c["metric_label"]};
            font-size: 0.75rem !important;
            font-weight: 500;
        }}
        div[data-testid="stMetricValue"] {{
            color: {c["metric_value"]};
            font-weight: 700 !important;
            font-size: 1.8rem !important;
            letter-spacing: -0.03em;
        }}
        div[data-testid="stMetricDelta"] {{
            color: {c["metric_delta"]};
            font-size: 0.8rem !important;
        }}

        /* ===== CARDS ===== */
        div.stDataFrame {{
            border: 1px solid {c["border"]};
            border-radius: 10px;
            overflow: hidden;
            transition: box-shadow 0.2s;
        }}
        div.stDataFrame:hover {{
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        div[data-testid="stExpander"] {{
            border: 1px solid {c["border"]};
            border-radius: 10px;
            background: {c["bg_secondary"]};
            transition: box-shadow 0.2s;
        }}
        div[data-testid="stExpander"]:hover {{
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }}

        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
            background: color-mix(in srgb, {c["text_primary"]} 4%, transparent);
            border-radius: 10px;
            padding: 3px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border-radius: 8px;
            padding: 0.4rem 0.9rem;
            color: {c["tab_inactive_color"]};
            font-size: 0.8rem;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: {c["text_primary"]};
            background: color-mix(in srgb, {c["text_primary"]} 6%, transparent);
        }}
        .stTabs [aria-selected="true"] {{
            background: {c["tab_active_bg"]} !important;
            color: white !important;
            font-weight: 600;
            box-shadow: 0 2px 8px color-mix(in srgb, {c["tab_active_bg"]} 30%, transparent);
        }}

        /* ===== BADGES / ALERTAS ===== */
        .stAlert {{
            background: {c["bg_secondary"]};
            border: 1px solid {c["border"]};
            border-radius: 10px;
            border-left: 4px solid {c["accent"]};
        }}
        .st-bp {{ background: {c["bg_primary"]}; }}

        /* ===== EXPANDER ===== */
        div[data-testid="stExpander"] div[data-testid="stExpanderToggleIcon"] svg {{
            fill: {c["text_primary"]};
        }}

        /* ===== RADIO / CHECKBOX ===== */
        .stRadio label, .stCheckbox label {{
            color: {c["text_primary"]} !important;
            font-size: 0.85rem;
        }}
        div[role="radiogroup"] label span:first-child {{
            background: {c["bg_secondary"]};
            border-color: {c["border"]};
        }}

        /* ===== SEPARATOR ===== */
        hr {{
            border: none;
            border-top: 1px solid {c["border"]};
            margin: 0.75rem 0;
        }}

        /* ===== SIDEBAR IDIOMA ===== */
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span {{
            font-size: 0.65rem !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
            min-height: 24px !important;
        }}

        /* ===== SIDEBAR TOGGLE / HAMBURGUER ===== */
        #MainMenu {{ visibility: hidden; display: none; }}
        .stDeployButton, .stAppDeployButton {{ display: none !important; }}

        /* ===== FILE UPLOADER ===== */
        .stFileUploader section {{
            border: 2px dashed {c["border"]};
            border-radius: 10px;
            background: color-mix(in srgb, {c["text_primary"]} 2%, transparent);
            transition: border-color 0.2s;
        }}
        .stFileUploader section:hover {{
            border-color: {c["accent"]};
        }}

        /* ===== PROGRESS BAR ===== */
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {c["accent"]}, {c["accent_hover"]});
            border-radius: 4px;
        }}

        /* ===== TABELAS ===== */
        table thead tr th {{
            background: {c["bg_secondary"]} !important;
            color: {c["text_primary"]} !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            border-bottom: 2px solid {c["border"]} !important;
        }}
        table tbody tr td {{
            border-bottom: 1px solid {c["border"]} !important;
            color: {c["text_primary"]} !important;
            font-size: 0.8rem !important;
        }}
        table tbody tr:hover {{
            background: color-mix(in srgb, {c["text_primary"]} 4%, transparent) !important;
        }}

        /* ===== SIDEBAR CORES GLOBAIS ===== */
        section[data-testid="stSidebar"] .st-emotion-cache-1wmy9hl,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {{
            color: {c["text_primary"]};
        }}

        /* ===== METRIC DELTA COR ===== */
        .st-emotion-cache-1wrc2r6 {{ color: {c["metric_label"]}; }}

        /* ===== BOTÃO LOGOUT ===== */
        button[key="nav_logout"] {{
            background: transparent !important;
            color: {c["text_secondary"]} !important;
            border: 1px solid {c["border"]} !important;
            font-weight: 400 !important;
            margin-top: 0.25rem !important;
        }}
        button[key="nav_logout"]:hover {{
            color: #e63946 !important;
            border-color: #e63946 !important;
            background: color-mix(in srgb, #e63946 8%, transparent) !important;
        }}

        .st-bv, .st-bu {{ border-color: {c["border"]}; }}

        /* ===== DASHBOARD CARDS ===== */
        .dash-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            border-color: {c["accent"]} !important;
        }}

        /* ===== TOOLTIP ===== */
        div[data-baseweb="tooltip"] {{
            background: {c["bg_secondary"]};
            border: 1px solid {c["border"]};
            border-radius: 8px;
            font-size: 0.8rem;
        }}

        /* ===== SIDEBAR BOTÃO CONFIG ===== */
        button[key="nav_config"] {{
            margin-top: 0.25rem !important;
        }}

        /* ===== CHART SELECTOR BUTTONS ===== */
        button[key^="chart_"] {{
            background: transparent !important;
            color: {c["text_primary"]} !important;
            border: 2px solid {c["border"]} !important;
            border-radius: 10px !important;
            padding: 0.5rem 0.25rem !important;
            text-align: center !important;
            font-size: 0.7rem !important;
            font-weight: 500 !important;
            line-height: 1.2 !important;
            white-space: normal !important;
            height: auto !important;
            min-height: 70px !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }}
        button[key^="chart_"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
            border-color: {c["accent"]} !important;
            background: color-mix(in srgb, {c["accent"]} 6%, transparent) !important;
        }}
        button[key^="chart_"] svg {{
            display: block;
            margin: 0 auto 0.25rem auto;
            color: {c["text_primary"]};
        }}
    </style>
    """

def seletor_tema():
    st.markdown("### 🎨 Tema")
    temas = obter_todos_temas()
    tema_atual = get_tema()
    opcoes = {k: f"{v['icone']} {v['nome']}" for k, v in temas.items()}

    escolha = st.selectbox(
        "Selecione o tema",
        options=list(opcoes.keys()),
        format_func=lambda k: opcoes[k],
        index=list(opcoes.keys()).index(tema_atual) if tema_atual in opcoes else 0,
        key="theme_selector"
    )
    if escolha and escolha != tema_atual:
        st.session_state.tema = escolha
        _salvar_pref(escolha, None)
        st.rerun()

    # Preview do tema atual
    tema_obj = temas.get(tema_atual)
    if tema_obj:
        cores = {k: v for k, v in tema_obj.items() if k not in ("nome", "icone")}
        st.markdown(f"**{t('tema.cores_atuais')}:**")
        cols = st.columns(4)
        for i, (chave, valor) in enumerate(sorted(cores.items())):
            with cols[i % 4]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0">'
                    f'<div style="width:16px;height:16px;border-radius:3px;background:{valor};border:1px solid #555"></div>'
                    f'<span style="font-size:0.75rem">{token_label(chave)}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    with st.expander(t("tema.criar_editar")):
        editor_tema_custom()

def _salvar_pref(tema=None, idioma=None):
    from modules.database import save_preferences
    save_preferences(tema=tema, idioma=idioma)

def editor_tema_custom():
    st.caption("Personalize todas as cores e salve como um novo tema.")

    # Carregar tema existente para editar, ou usar o atual como base
    editando = st.session_state.get("editando_tema_key", "")
    temas = obter_todos_temas()
    tema_base = temas.get(editando, get_cores())

    with st.form("custom_theme_form"):
        nome = st.text_input("Nome do tema", value=tema_base.get("nome", ""),
                             placeholder="Ex: Minha Empresa")

        col1, col2 = st.columns(2)
        cores_editadas = {}
        tokens_mostrar = [
            ("bg_primary", token_label("bg_primary")),
            ("bg_secondary", token_label("bg_secondary")),
            ("text_primary", token_label("text_primary")),
            ("text_secondary", token_label("text_secondary")),
            ("accent", token_label("accent")),
            ("accent_hover", token_label("accent_hover")),
            ("border", token_label("border")),
            ("metric_label", token_label("metric_label")),
            ("metric_value", token_label("metric_value")),
            ("metric_delta", token_label("metric_delta")),
            ("card_bg", token_label("card_bg")),
            ("card_border", token_label("card_border")),
            ("tab_inactive_bg", token_label("tab_inactive_bg")),
            ("tab_inactive_color", token_label("tab_inactive_color")),
            ("tab_active_bg", token_label("tab_active_bg")),
        ]

        tema_atual = get_tema()
        for i, (token, rotulo) in enumerate(tokens_mostrar):
            with (col1 if i < 8 else col2):
                cores_editadas[token] = st.color_picker(
                    rotulo,
                    value=tema_base.get(token, "#000000"),
                    key=f"cp_{tema_atual}_{token}"
                )

        salvar = st.form_submit_button(t("tema.salvar"), type="primary", use_container_width=True)

        if salvar and nome.strip():
            chave = editando if editando else f"custom_{len([k for k in temas if k.startswith('custom_')])}"
            if not editando:
                chave = f"custom_{len([k for k in temas if k.startswith('custom_')]) + 1}"

            novo_tema = {"nome": nome.strip(), "icone": "🎨"}
            novo_tema.update(cores_editadas)

            custom = dict(st.session_state.get(CHAVE_CUSTOM, {}))
            custom[chave] = novo_tema
            st.session_state[CHAVE_CUSTOM] = custom
            st.session_state.tema = chave
            st.session_state.pop("editando_tema_key", None)
            st.success(f"Tema '{nome}' salvo!")
            st.rerun()

    # Gerenciar temas customizados
    custom = st.session_state.get(CHAVE_CUSTOM, {})
    if custom:
        st.markdown("---")
        st.markdown(f"**{t('tema.excluir')}**")
        for chave in list(custom.keys()):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"🎨 {custom[chave]['nome']}")
            with col_b:
                if st.button("🗑️", key=f"del_theme_{chave}"):
                    custom.pop(chave, None)
                    st.session_state[CHAVE_CUSTOM] = custom
                    st.rerun()
