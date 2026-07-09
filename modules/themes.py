import streamlit as st
import json

TEMAS_PADRAO = {
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
        st.rerun()

    # Preview do tema atual
    tema_obj = temas.get(tema_atual)
    if tema_obj:
        cores = {k: v for k, v in tema_obj.items() if k not in ("nome", "icone")}
        st.markdown("**Cores do tema atual:**")
        cols = st.columns(4)
        for i, (chave, valor) in enumerate(sorted(cores.items())):
            with cols[i % 4]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0">'
                    f'<div style="width:16px;height:16px;border-radius:3px;background:{valor};border:1px solid #555"></div>'
                    f'<span style="font-size:0.75rem">{chave}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    with st.expander("✏️ Criar / Editar tema personalizado"):
        editor_tema_custom()

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
            ("bg_primary", "Fundo principal"),
            ("bg_secondary", "Fundo cards/sidebar"),
            ("text_primary", "Texto principal"),
            ("text_secondary", "Texto secundário"),
            ("accent", "Cor de destaque"),
            ("accent_hover", "Destaque hover"),
            ("border", "Bordas"),
            ("metric_label", "Label de métrica"),
            ("metric_value", "Valor de métrica"),
            ("metric_delta", "Delta de métrica"),
            ("card_bg", "Fundo do card"),
            ("card_border", "Borda do card"),
            ("tab_inactive_bg", "Aba inativa fundo"),
            ("tab_inactive_color", "Aba inativa texto"),
            ("tab_active_bg", "Aba ativa fundo"),
        ]

        for i, (token, rotulo) in enumerate(tokens_mostrar):
            with (col1 if i < 8 else col2):
                cores_editadas[token] = st.color_picker(
                    rotulo,
                    value=tema_base.get(token, "#000000"),
                    key=f"cp_{token}"
                )

        salvar = st.form_submit_button("💾 Salvar tema personalizado", type="primary", use_container_width=True)

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
        st.markdown("**Excluir temas personalizados**")
        for chave in list(custom.keys()):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"🎨 {custom[chave]['nome']}")
            with col_b:
                if st.button("🗑️", key=f"del_theme_{chave}"):
                    custom.pop(chave, None)
                    st.session_state[CHAVE_CUSTOM] = custom
                    st.rerun()
