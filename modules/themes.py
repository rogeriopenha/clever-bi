import streamlit as st
import json
from modules.i18n import t, token_label

TEMAS_PADRAO = {
    "clever_dark": {
        "nome": "CLEVER Dark", "icone": "🌙",
        "bg_primary": "#0f1629", "bg_secondary": "#1a2340",
        "text_primary": "#e8edf5", "text_secondary": "#6b7fa3",
        "accent": "#4a7cf7", "accent_hover": "#5a8cf7",
        "border": "#2a3450",
        "metric_label": "#8899b8", "metric_value": "#e8edf5", "metric_delta": "#4a7cf7",
        "card_bg": "#1a2340", "card_border": "#2a3450",
        "tab_inactive_bg": "#1a2340", "tab_inactive_color": "#8899b8", "tab_active_bg": "#4a7cf7",
    },
    "clever_light": {
        "nome": "CLEVER Light", "icone": "☀️",
        "bg_primary": "#f5f7fa", "bg_secondary": "#ffffff",
        "text_primary": "#1a2340", "text_secondary": "#6b7fa3",
        "accent": "#4a7cf7", "accent_hover": "#3a6ce7",
        "border": "#d1d9e6",
        "metric_label": "#6b7fa3", "metric_value": "#1a2340", "metric_delta": "#4a7cf7",
        "card_bg": "#ffffff", "card_border": "#d1d9e6",
        "tab_inactive_bg": "#e8edf5", "tab_inactive_color": "#6b7fa3", "tab_active_bg": "#4a7cf7",
    },
    "midnight": {
        "nome": "Midnight", "icone": "🌌",
        "bg_primary": "#0a0a1a", "bg_secondary": "#12122a",
        "text_primary": "#e0e0ff", "text_secondary": "#8888bb",
        "accent": "#7c4dff", "accent_hover": "#8c5dff",
        "border": "#2a2a4a",
        "metric_label": "#8888bb", "metric_value": "#e0e0ff", "metric_delta": "#7c4dff",
        "card_bg": "#12122a", "card_border": "#2a2a4a",
        "tab_inactive_bg": "#12122a", "tab_inactive_color": "#8888bb", "tab_active_bg": "#7c4dff",
    },
    "forest": {
        "nome": "Forest", "icone": "🌿",
        "bg_primary": "#0f1a12", "bg_secondary": "#1a2a1e",
        "text_primary": "#e0f0e4", "text_secondary": "#7a9a7a",
        "accent": "#2ecc71", "accent_hover": "#3edc81",
        "border": "#2a3a2e",
        "metric_label": "#7a9a7a", "metric_value": "#e0f0e4", "metric_delta": "#2ecc71",
        "card_bg": "#1a2a1e", "card_border": "#2a3a2e",
        "tab_inactive_bg": "#1a2a1e", "tab_inactive_color": "#7a9a7a", "tab_active_bg": "#2ecc71",
    },
    "sunset": {
        "nome": "Sunset", "icone": "🌅",
        "bg_primary": "#1a0f0f", "bg_secondary": "#2a1a1a",
        "text_primary": "#f5e0d0", "text_secondary": "#b08070",
        "accent": "#e67e22", "accent_hover": "#f08e32",
        "border": "#3a2a20",
        "metric_label": "#b08070", "metric_value": "#f5e0d0", "metric_delta": "#e67e22",
        "card_bg": "#2a1a1a", "card_border": "#3a2a20",
        "tab_inactive_bg": "#2a1a1a", "tab_inactive_color": "#b08070", "tab_active_bg": "#e67e22",
    },
    "ocean": {
        "nome": "Ocean", "icone": "🌊",
        "bg_primary": "#0a1628", "bg_secondary": "#0f1f3a",
        "text_primary": "#d4e8ff", "text_secondary": "#7a9ec4",
        "accent": "#00b4d8", "accent_hover": "#00c8e8",
        "border": "#1a3450",
        "metric_label": "#7a9ec4", "metric_value": "#d4e8ff", "metric_delta": "#00b4d8",
        "card_bg": "#0f1f3a", "card_border": "#1a3450",
        "tab_inactive_bg": "#0f1f3a", "tab_inactive_color": "#7a9ec4", "tab_active_bg": "#00b4d8",
    },
    "cherry": {
        "nome": "Cherry", "icone": "🍒",
        "bg_primary": "#1a0a0f", "bg_secondary": "#2a1018",
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
        "bg_primary": "#1e1124", "bg_secondary": "#2d1b36",
        "text_primary": "#f0e0f8", "text_secondary": "#a080b8",
        "accent": "#bd93f9", "accent_hover": "#cfa3ff",
        "border": "#3a2848",
        "metric_label": "#a080b8", "metric_value": "#f0e0f8", "metric_delta": "#bd93f9",
        "card_bg": "#2d1b36", "card_border": "#3a2848",
        "tab_inactive_bg": "#2d1b36", "tab_inactive_color": "#a080b8", "tab_active_bg": "#bd93f9",
    },
    "corporate": {
        "nome": "Corporate", "icone": "🏢",
        "bg_primary": "#eef1f5", "bg_secondary": "#ffffff",
        "text_primary": "#1a2a3a", "text_secondary": "#5a7a9a",
        "accent": "#1a6bc4", "accent_hover": "#2a7bd4",
        "border": "#c0c8d4",
        "metric_label": "#5a7a9a", "metric_value": "#1a2a3a", "metric_delta": "#1a6bc4",
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
        .stApp {{ background-color: {c["bg_primary"]}; }}
        .stSidebar {{ background-color: {c["bg_secondary"]}; }}
        h1, h2, h3, h4, h5, h6 {{ color: {c["text_primary"]} !important; }}
        p, li, span, div, label, .st-emotion-cache-15tx938, .st-emotion-cache-1inwz65 {{
            color: {c["text_primary"]};
        }}
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
        .stSelectbox div[data-baseweb="select"],
        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: {c["bg_secondary"]} !important;
            color: {c["text_primary"]} !important;
            border: 1px solid {c["border"]};
            border-radius: 8px;
        }}
        .stSelectbox div[data-baseweb="select"] span {{
            color: {c["text_primary"]} !important;
        }}
        .stSelectbox li[role="option"] {{
            background-color: {c["bg_secondary"]} !important;
            color: {c["text_primary"]} !important;
        }}
        .stSelectbox li[role="option"]:hover {{
            background-color: {c["accent"]} !important;
            color: white !important;
        }}
        .stMultiSelect div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"] span {{
            background-color: {c["bg_secondary"]} !important;
            color: {c["text_primary"]} !important;
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
        section[data-testid="stSidebar"] .st-emotion-cache-1wmy9hl,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {{
            color: {c["text_primary"]};
        }}
        hr {{ border-color: {c["border"]}; }}
        .st-emotion-cache-1mi2ry5 {{ background-color: {c["bg_secondary"]}; }}
        .stAlert {{ background-color: {c["bg_secondary"]}; border: 1px solid {c["border"]}; }}
        .st-bp {{ background-color: {c["bg_primary"]}; }}
        div[data-testid="stExpander"] div[data-testid="stExpanderToggleIcon"] svg {{
            fill: {c["text_primary"]};
        }}
        .stNumberInput input, .stDateInput input, .stTimeInput input {{
            background-color: {c["bg_secondary"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
        }}
        .stRadio label, .stCheckbox label {{
            color: {c["text_primary"]} !important;
        }}
        div[role="radiogroup"] label span:first-child {{
            background-color: {c["bg_secondary"]};
            border-color: {c["border"]};
        }}
        .st-bv, .st-bu {{ border-color: {c["border"]}; }}
        /* Fonte menor e mais compacta para o seletor de idioma na sidebar */
        section[data-testid="stSidebar"] > div:first-child {{
            padding-top: 0 !important;
            margin-top: 0 !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span {{
            font-size: 0.65rem !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
            min-height: 24px !important;
        }}
        /* Esconder toolbar superior do Streamlit */
        #MainMenu {{ visibility: hidden; display: none; }}
        .stDeployButton, .stAppDeployButton {{ display: none !important; }}
        header[data-testid="stHeader"] {{ display: none !important; }}
        div[data-testid="stToolbar"] {{ display: none !important; }}
        button[kind="header"] {{ display: none !important; }}
        .st-emotion-cache-1dp5vir {{ display: none !important; }}
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
