import streamlit as st

TEMAS = {
    "clever_dark": {
        "nome": "CLEVER Dark",
        "icone": "🌙",
        "bg_primary": "#0f1629",
        "bg_secondary": "#1a2340",
        "text_primary": "#e8edf5",
        "text_secondary": "#6b7fa3",
        "accent": "#4a7cf7",
        "accent_hover": "#5a8cf7",
        "border": "#2a3450",
        "metric_label": "#8899b8",
        "metric_value": "#e8edf5",
        "metric_delta": "#4a7cf7",
        "card_bg": "#1a2340",
        "card_border": "#2a3450",
        "tab_inactive_bg": "#1a2340",
        "tab_inactive_color": "#8899b8",
        "tab_active_bg": "#4a7cf7",
    },
    "clever_light": {
        "nome": "CLEVER Light",
        "icone": "☀️",
        "bg_primary": "#f5f7fa",
        "bg_secondary": "#ffffff",
        "text_primary": "#1a2340",
        "text_secondary": "#6b7fa3",
        "accent": "#4a7cf7",
        "accent_hover": "#3a6ce7",
        "border": "#d1d9e6",
        "metric_label": "#6b7fa3",
        "metric_value": "#1a2340",
        "metric_delta": "#4a7cf7",
        "card_bg": "#ffffff",
        "card_border": "#d1d9e6",
        "tab_inactive_bg": "#e8edf5",
        "tab_inactive_color": "#6b7fa3",
        "tab_active_bg": "#4a7cf7",
    },
    "midnight": {
        "nome": "Midnight",
        "icone": "🌌",
        "bg_primary": "#0a0a1a",
        "bg_secondary": "#12122a",
        "text_primary": "#e0e0ff",
        "text_secondary": "#8888bb",
        "accent": "#7c4dff",
        "accent_hover": "#8c5dff",
        "border": "#2a2a4a",
        "metric_label": "#8888bb",
        "metric_value": "#e0e0ff",
        "metric_delta": "#7c4dff",
        "card_bg": "#12122a",
        "card_border": "#2a2a4a",
        "tab_inactive_bg": "#12122a",
        "tab_inactive_color": "#8888bb",
        "tab_active_bg": "#7c4dff",
    },
    "forest": {
        "nome": "Forest",
        "icone": "🌿",
        "bg_primary": "#0f1a12",
        "bg_secondary": "#1a2a1e",
        "text_primary": "#e0f0e4",
        "text_secondary": "#7a9a7a",
        "accent": "#2ecc71",
        "accent_hover": "#3edc81",
        "border": "#2a3a2e",
        "metric_label": "#7a9a7a",
        "metric_value": "#e0f0e4",
        "metric_delta": "#2ecc71",
        "card_bg": "#1a2a1e",
        "card_border": "#2a3a2e",
        "tab_inactive_bg": "#1a2a1e",
        "tab_inactive_color": "#7a9a7a",
        "tab_active_bg": "#2ecc71",
    },
    "sunset": {
        "nome": "Sunset",
        "icone": "🌅",
        "bg_primary": "#1a0f0f",
        "bg_secondary": "#2a1a1a",
        "text_primary": "#f5e0d0",
        "text_secondary": "#b08070",
        "accent": "#e67e22",
        "accent_hover": "#f08e32",
        "border": "#3a2a20",
        "metric_label": "#b08070",
        "metric_value": "#f5e0d0",
        "metric_delta": "#e67e22",
        "card_bg": "#2a1a1a",
        "card_border": "#3a2a20",
        "tab_inactive_bg": "#2a1a1a",
        "tab_inactive_color": "#b08070",
        "tab_active_bg": "#e67e22",
    },
}

TEMA_PADRAO = "clever_dark"

def get_tema() -> str:
    tema = st.session_state.get("tema", TEMA_PADRAO)
    if tema not in TEMAS:
        tema = TEMA_PADRAO
    return tema

def get_cores() -> dict:
    return TEMAS[get_tema()]

def css_tema() -> str:
    c = get_cores()
    return f"""
    <style>
        .stApp {{ background-color: {c["bg_primary"]}; }}
        .stSidebar {{ background-color: {c["bg_secondary"]}; }}
        h1, h2, h3, h4, h5, h6 {{ color: {c["text_primary"]} !important; }}
        p, li, span, div, label {{ color: {c["text_primary"]}; }}
        .st-bw {{ background-color: {c["bg_secondary"]}; }}
        .stButton button {{
            background-color: {c["accent"]};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }}
        .stButton button:hover {{ background-color: {c["accent_hover"]}; }}
        .stTextInput input {{
            background-color: {c["bg_secondary"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
            border-radius: 8px;
        }}
        .stTextArea textarea {{
            background-color: {c["bg_secondary"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
        }}
        .stSelectbox div[data-baseweb="select"] {{
            background-color: {c["bg_secondary"]};
            border: 1px solid {c["border"]};
            border-radius: 8px;
        }}
        .st-emotion-cache-1wrc2r6 {{ color: {c["metric_label"]}; }}
        div[data-testid="stMetricLabel"] {{ color: {c["metric_label"]}; }}
        div[data-testid="stMetricValue"] {{ color: {c["metric_value"]}; font-weight: 700; }}
        div[data-testid="stMetricDelta"] {{ color: {c["metric_delta"]}; }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 0; }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {c["tab_inactive_bg"]};
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
            color: {c["tab_inactive_color"]};
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {c["tab_active_bg"]};
            color: white !important;
        }}
        div.stDataFrame {{ border: 1px solid {c["border"]}; border-radius: 8px; }}
        section[data-testid="stSidebar"] .st-emotion-cache-1wmy9hl {{ color: {c["text_secondary"]}; }}
        hr {{ border-color: {c["border"]}; }}
        .st-emotion-cache-1mi2ry5 {{ background-color: {c["bg_secondary"]}; }}
    </style>
    """

def seletor_tema():
    st.markdown("### 🎨 Tema")
    tema_atual = get_tema()
    opcoes = {k: f"{v['icone']} {v['nome']}" for k, v in TEMAS.items()}
    escolha = st.selectbox(
        "Selecione o tema",
        options=list(opcoes.keys()),
        format_func=lambda k: opcoes[k],
        index=list(opcoes.keys()).index(tema_atual) if tema_atual in opcoes else 0,
        key="theme_selector"
    )
    if escolha and escolha != tema_atual:
        st.session_state.tema = escolha
        st.rerun()
