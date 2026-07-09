import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

def render_widget(widget: dict, dados: pd.DataFrame):
    tipo = widget.get("tipo", "kpi")
    config = widget.get("config", {})
    if isinstance(config, str):
        config = json.loads(config)
    titulo = widget.get("titulo", "Widget")

    with st.container():
        if tipo == "kpi":
            render_kpi(titulo, dados, config)
        elif tipo == "bar":
            render_bar(titulo, dados, config)
        elif tipo == "line":
            render_line(titulo, dados, config)
        elif tipo == "pie":
            render_pie(titulo, dados, config)
        elif tipo == "table":
            render_table(titulo, dados, config)
        elif tipo == "metric":
            render_metric(titulo, dados, config)

def render_kpi(titulo, dados, config):
    col_valor = config.get("coluna_valor")
    col_meta = config.get("coluna_meta")
    prefixo = config.get("prefixo", "")
    sufixo = config.get("sufixo", "")

    valor = dados[col_valor].sum() if col_valor and col_valor in dados.columns else len(dados)
    meta = dados[col_meta].sum() if col_meta and col_meta in dados.columns else None

    delta = None
    if meta and meta > 0:
        delta = f"{((valor - meta) / meta * 100):.1f}% vs meta"

    st.markdown(f"<h4 style='color:#8899b8;margin-bottom:0'>{titulo}</h4>", unsafe_allow_html=True)
    st.metric(
        label="",
        value=f"{prefixo}{valor:,.0f}{sufixo}",
        delta=delta,
        delta_color="normal"
    )

def render_bar(titulo, dados, config):
    x = config.get("coluna_x")
    y = config.get("coluna_y")
    cor = config.get("cor", "#4a7cf7")
    orient = config.get("orientacao", "v")

    if not x or not y:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if x not in dados.columns or y not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    fig = px.bar(dados, x=x, y=y, title=titulo, orientation=orient,
                 color_discrete_sequence=[cor],
                 text_auto=True)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf5"),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_line(titulo, dados, config):
    x = config.get("coluna_x")
    y = config.get("coluna_y")
    cor = config.get("cor", "#4a7cf7")

    if not x or not y:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if x not in dados.columns or y not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    fig = px.line(dados, x=x, y=y, title=titulo,
                  color_discrete_sequence=[cor],
                  markers=True)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf5"),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_pie(titulo, dados, config):
    nomes = config.get("coluna_nomes")
    valores = config.get("coluna_valores")

    if not nomes or not valores:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if nomes not in dados.columns or valores not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    fig = px.pie(dados, names=nomes, values=valores, title=titulo)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf5"),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_table(titulo, dados, config):
    colunas = config.get("colunas", [])
    max_rows = config.get("max_rows", 100)

    if colunas:
        cols_existentes = [c for c in colunas if c in dados.columns]
        if cols_existentes:
            dados = dados[cols_existentes]

    st.markdown(f"<h4 style='color:#8899b8'>{titulo}</h4>", unsafe_allow_html=True)
    st.dataframe(dados.head(max_rows), use_container_width=True, height=min(400, 35 * min(len(dados), max_rows)))

def render_metric(titulo, dados, config):
    col_valor = config.get("coluna_valor")
    col_categoria = config.get("coluna_categoria")
    col_meta = config.get("coluna_meta")

    if not col_valor or not col_categoria:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if col_valor not in dados.columns or col_categoria not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    agrupado = dados.groupby(col_categoria)[col_valor].sum().reset_index()
    cols = st.columns(min(len(agrupado), 4))
    for i, (_, row) in enumerate(agrupado.iterrows()):
        with cols[i % len(cols)]:
            st.markdown(f"<p style='color:#6b7fa3;font-size:0.8rem;margin-bottom:0'>{row[col_categoria]}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:1.5rem;font-weight:700;color:#e8edf5'>{row[col_valor]:,.0f}</p>", unsafe_allow_html=True)

def editor_widget(widget_data: dict = None) -> dict:
    st.markdown("### ⚙️ Configurar Widget")

    tipo = st.selectbox("Tipo de gráfico",
        ["kpi", "bar", "line", "pie", "table", "metric"],
        index=0 if not widget_data else ["kpi", "bar", "line", "pie", "table", "metric"].index(widget_data.get("tipo", "kpi")))

    titulo = st.text_input("Título", value=widget_data.get("titulo", "") if widget_data else "")

    config = {}
    if widget_data and isinstance(widget_data.get("config"), dict):
        config = widget_data["config"]

    with st.expander("Configuração do gráfico", expanded=True):
        if tipo in ("kpi", "metric"):
            config["coluna_valor"] = st.text_input("Coluna de valor", value=config.get("coluna_valor", ""))
            if tipo == "kpi":
                config["coluna_meta"] = st.text_input("Coluna de meta (opcional)", value=config.get("coluna_meta", ""))
            else:
                config["coluna_categoria"] = st.text_input("Coluna de categoria", value=config.get("coluna_categoria", ""))
            config["prefixo"] = st.text_input("Prefixo (ex: R$)", value=config.get("prefixo", ""))
            config["sufixo"] = st.text_input("Sufixo (ex: %)", value=config.get("sufixo", ""))
        elif tipo in ("bar", "line"):
            config["coluna_x"] = st.text_input("Coluna X (categoria)", value=config.get("coluna_x", ""))
            config["coluna_y"] = st.text_input("Coluna Y (valor)", value=config.get("coluna_y", ""))
            config["cor"] = st.color_picker("Cor", value=config.get("cor", "#4a7cf7"))
            if tipo == "bar":
                config["orientacao"] = st.radio("Orientação", ["v", "h"], horizontal=True)
        elif tipo == "pie":
            config["coluna_nomes"] = st.text_input("Coluna de nomes", value=config.get("coluna_nomes", ""))
            config["coluna_valores"] = st.text_input("Coluna de valores", value=config.get("coluna_valores", ""))
        elif tipo == "table":
            config["colunas"] = st.text_input("Colunas (separadas por vírgula)", value=",".join(config.get("colunas", [])))
            config["max_rows"] = st.number_input("Máximo de linhas", value=config.get("max_rows", 100))

    return {
        "tipo": tipo,
        "titulo": titulo,
        "config": config
    }
