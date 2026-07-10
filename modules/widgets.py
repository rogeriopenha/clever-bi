import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

PALETA = px.colors.qualitative.Plotly

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
        elif tipo == "area":
            render_area(titulo, dados, config)
        elif tipo == "pie":
            render_pie(titulo, dados, config)
        elif tipo == "scatter":
            render_scatter(titulo, dados, config)
        elif tipo == "histogram":
            render_histogram(titulo, dados, config)
        elif tipo == "heatmap":
            render_heatmap(titulo, dados, config)
        elif tipo == "funnel":
            render_funnel(titulo, dados, config)
        elif tipo == "gauge":
            render_gauge(titulo, dados, config)
        elif tipo == "treemap":
            render_treemap(titulo, dados, config)
        elif tipo == "sunburst":
            render_sunburst(titulo, dados, config)
        elif tipo == "waterfall":
            render_waterfall(titulo, dados, config)
        elif tipo == "map":
            render_map(titulo, dados, config)
        elif tipo == "table":
            render_table(titulo, dados, config)
        elif tipo == "metric":
            render_metric(titulo, dados, config)

def _layout_padrao(titulo):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf5"),
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text=titulo, font=dict(size=14, color="#8899b8"))
    )

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
    agrupar = config.get("coluna_agrupar")
    empilhar = config.get("empilhar", False)

    if not x or not y:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if x not in dados.columns or y not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    if agrupar and agrupar in dados.columns:
        barmode = "stack" if empilhar else "group"
        fig = px.bar(dados, x=x, y=y, color=agrupar, title=titulo,
                     orientation=orient, barmode=barmode,
                     text_auto=True, color_discrete_sequence=PALETA)
    else:
        fig = px.bar(dados, x=x, y=y, title=titulo, orientation=orient,
                     color_discrete_sequence=[cor], text_auto=True)
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_line(titulo, dados, config):
    x = config.get("coluna_x")
    y = config.get("coluna_y")
    cor = config.get("cor", "#4a7cf7")
    agrupar = config.get("coluna_agrupar")

    if not x or not y:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if x not in dados.columns or y not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    if agrupar and agrupar in dados.columns:
        fig = px.line(dados, x=x, y=y, color=agrupar, title=titulo,
                      markers=True, color_discrete_sequence=PALETA)
    else:
        fig = px.line(dados, x=x, y=y, title=titulo,
                      color_discrete_sequence=[cor], markers=True)
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_area(titulo, dados, config):
    x = config.get("coluna_x")
    y = config.get("coluna_y")
    agrupar = config.get("coluna_agrupar")

    if not x or not y:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if x not in dados.columns or y not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    if agrupar and agrupar in dados.columns:
        fig = px.area(dados, x=x, y=y, color=agrupar, title=titulo,
                      color_discrete_sequence=PALETA)
    else:
        fig = px.area(dados, x=x, y=y, title=titulo, color_discrete_sequence=PALETA[:1])
    fig.update_layout(**_layout_padrao(titulo))
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

    fig = px.pie(dados, names=nomes, values=valores, title=titulo,
                 color_discrete_sequence=PALETA, hole=config.get("donut", 0))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8edf5"),
                      margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

def render_scatter(titulo, dados, config):
    x = config.get("coluna_x")
    y = config.get("coluna_y")
    tamanho = config.get("coluna_tamanho")
    cor = config.get("coluna_cor")
    if not x or not y:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if x not in dados.columns or y not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    fig = px.scatter(dados, x=x, y=y, size=tamanho if tamanho in dados.columns else None,
                     color=cor if cor in dados.columns else None,
                     title=titulo, color_discrete_sequence=PALETA,
                     trendline=config.get("tendencia", None))
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_histogram(titulo, dados, config):
    x = config.get("coluna_x")
    nbins = config.get("nbins", 20)
    if not x or x not in dados.columns:
        st.info(f"Configure coluna para '{titulo}'")
        return
    fig = px.histogram(dados, x=x, nbins=nbins, title=titulo,
                       color=config.get("coluna_agrupar") if config.get("coluna_agrupar") in dados.columns else None,
                       color_discrete_sequence=PALETA)
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_heatmap(titulo, dados, config):
    x = config.get("coluna_x")
    y = config.get("coluna_y")
    z = config.get("coluna_z")
    if not all(c in dados.columns for c in [x, y, z] if c):
        st.info(f"Configure 3 colunas (X, Y, Z) para '{titulo}'")
        return
    pivot = dados.pivot_table(index=y, columns=x, values=z, aggfunc=config.get("agregacao", "mean"))
    fig = px.imshow(pivot, text_auto=config.get("texto", False),
                    title=titulo, color_continuous_scale=config.get("escala", "Viridis"))
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_funnel(titulo, dados, config):
    x = config.get("coluna_valores")
    y = config.get("coluna_nomes")
    if not x or not y:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if x not in dados.columns or y not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return
    fig = px.funnel(dados, x=x, y=y, title=titulo, color_discrete_sequence=PALETA)
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_gauge(titulo, dados, config):
    col_valor = config.get("coluna_valor")
    if not col_valor or col_valor not in dados.columns:
        st.info(f"Configure coluna para '{titulo}'")
        return
    valor = dados[col_valor].sum()
    minimo = config.get("min", 0)
    maximo = config.get("max", valor * 1.5 if valor > 0 else 100)
    passo = config.get("passo", maximo / 5)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        domain=dict(x=[0, 1], y=[0, 1]),
        title=dict(text=titulo, font=dict(color="#8899b8", size=14)),
        delta=dict(reference=config.get("meta", maximo * 0.8)),
        gauge=dict(
            axis=dict(range=[minimo, maximo], tickwidth=1, tickcolor="#6b7fa3"),
            bar=dict(color=config.get("cor", "#4a7cf7")),
            bgcolor="#1a2340",
            borderwidth=1, bordercolor="#2a3450",
            steps=[
                dict(range=[minimo, maximo * 0.5], color="#1a2a40"),
                dict(range=[maximo * 0.5, maximo * 0.8], color="#1a3040"),
            ],
            threshold=dict(
                line=dict(color="red", width=3),
                thickness=0.75, value=maximo * 0.9
            )
        )
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8edf5"),
                      height=250, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

def render_treemap(titulo, dados, config):
    valores = config.get("coluna_valores")
    categorias = [v for k, v in config.items() if k.startswith("nivel") and v]
    if not valores or valores not in dados.columns:
        st.info(f"Configure colunas para '{titulo}'")
        return
    cats = [c for c in categorias if c in dados.columns]
    if not cats:
        st.info("Adicione ao menos um nível hierárquico")
        return
    fig = px.treemap(dados, path=cats, values=valores, title=titulo,
                     color=valores, color_continuous_scale=config.get("escala", "Viridis"))
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_sunburst(titulo, dados, config):
    valores = config.get("coluna_valores")
    categorias = [v for k, v in config.items() if k.startswith("nivel") and v]
    if not valores or valores not in dados.columns:
        st.info(f"Configure colunas para '{titulo}'")
        return
    cats = [c for c in categorias if c in dados.columns]
    if not cats:
        st.info("Adicione ao menos um nível hierárquico")
        return
    fig = px.sunburst(dados, path=cats, values=valores, title=titulo,
                      color=valores, color_continuous_scale=config.get("escala", "Viridis"))
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_waterfall(titulo, dados, config):
    x = config.get("coluna_x")
    y = config.get("coluna_y")
    if not x or not y:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if x not in dados.columns or y not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return

    fig = go.Figure(go.Waterfall(
        name=titulo, orientation="v",
        measure=[("relative" if v >= 0 else "relative") for v in dados[y]],
        x=dados[x], y=dados[y],
        text=[f"{v:,.0f}" for v in dados[y]],
        textposition="outside",
        connector=dict(line=dict(color="#6b7fa3", width=1))
    ))
    fig.update_layout(**_layout_padrao(titulo))
    st.plotly_chart(fig, use_container_width=True)

def render_map(titulo, dados, config):
    lat = config.get("coluna_lat")
    lon = config.get("coluna_lon")
    cor = config.get("coluna_cor")
    tamanho = config.get("coluna_tamanho")
    if not lat or not lon:
        st.info(f"Configure colunas de latitude/longitude para '{titulo}'")
        return
    if lat not in dados.columns or lon not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return
    fig = px.scatter_mapbox(dados, lat=lat, lon=lon,
                            color=cor if cor in dados.columns else None,
                            size=tamanho if tamanho in dados.columns else None,
                            title=titulo, zoom=config.get("zoom", 4),
                            mapbox_style=config.get("estilo", "carto-positron"),
                            color_continuous_scale=PALETA)
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), font=dict(color="#e8edf5"))
    st.plotly_chart(fig, use_container_width=True)

def render_table(titulo, dados, config):
    colunas = config.get("colunas", [])
    max_rows = config.get("max_rows", 100)
    if colunas:
        cols_existentes = [c for c in colunas if c in dados.columns]
        if cols_existentes:
            dados = dados[cols_existentes]
    st.markdown(f"<h4 style='color:#8899b8'>{titulo}</h4>", unsafe_allow_html=True)
    st.dataframe(dados.head(max_rows), use_container_width=True,
                 height=min(400, 35 * min(len(dados), max_rows)))

def render_metric(titulo, dados, config):
    col_valor = config.get("coluna_valor")
    col_categoria = config.get("coluna_categoria")
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

    TIPOS = ["kpi", "bar", "line", "area", "pie", "scatter", "histogram",
             "heatmap", "funnel", "gauge", "treemap", "sunburst", "waterfall",
             "map", "table", "metric"]

    tipo_atual = widget_data.get("tipo", "kpi") if widget_data else "kpi"
    tipo = st.selectbox("Tipo de gráfico", TIPOS,
                        index=TIPOS.index(tipo_atual) if tipo_atual in TIPOS else 0)

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

        elif tipo in ("bar", "line", "area"):
            config["coluna_x"] = st.text_input("Coluna X (categoria)", value=config.get("coluna_x", ""))
            config["coluna_y"] = st.text_input("Coluna Y (valor)", value=config.get("coluna_y", ""))
            config["coluna_agrupar"] = st.text_input("Agrupar por (opcional)", value=config.get("coluna_agrupar", ""))
            config["cor"] = st.color_picker("Cor", value=config.get("cor", "#4a7cf7"))
            if tipo == "bar":
                config["orientacao"] = st.radio("Orientação", ["v", "h"], horizontal=True)
                config["empilhar"] = st.checkbox("Empilhar grupos", value=config.get("empilhar", False))

        elif tipo == "scatter":
            config["coluna_x"] = st.text_input("Coluna X", value=config.get("coluna_x", ""))
            config["coluna_y"] = st.text_input("Coluna Y", value=config.get("coluna_y", ""))
            config["coluna_tamanho"] = st.text_input("Tamanho do ponto (opcional)", value=config.get("coluna_tamanho", ""))
            config["coluna_cor"] = st.text_input("Cor por categoria (opcional)", value=config.get("coluna_cor", ""))
            config["tendencia"] = st.selectbox("Linha de tendência", [None, "ols", "lowess"],
                                               index=0 if not config.get("tendencia") else [None, "ols", "lowess"].index(config["tendencia"]))

        elif tipo == "histogram":
            config["coluna_x"] = st.text_input("Coluna para distribuição", value=config.get("coluna_x", ""))
            config["nbins"] = st.number_input("Número de bins", value=config.get("nbins", 20))
            config["coluna_agrupar"] = st.text_input("Agrupar por (opcional)", value=config.get("coluna_agrupar", ""))

        elif tipo == "heatmap":
            config["coluna_x"] = st.text_input("Coluna X (linhas)", value=config.get("coluna_x", ""))
            config["coluna_y"] = st.text_input("Coluna Y (colunas)", value=config.get("coluna_y", ""))
            config["coluna_z"] = st.text_input("Coluna Z (valor)", value=config.get("coluna_z", ""))
            config["agregacao"] = st.selectbox("Agregação", ["mean", "sum", "count", "max", "min"],
                                               index=["mean", "sum", "count", "max", "min"].index(config.get("agregacao", "mean")))
            config["texto"] = st.checkbox("Mostrar valores", value=config.get("texto", False))

        elif tipo == "funnel":
            config["coluna_nomes"] = st.text_input("Coluna de etapas", value=config.get("coluna_nomes", ""))
            config["coluna_valores"] = st.text_input("Coluna de valores", value=config.get("coluna_valores", ""))

        elif tipo == "gauge":
            config["coluna_valor"] = st.text_input("Coluna de valor", value=config.get("coluna_valor", ""))
            config["min"] = st.number_input("Valor mínimo", value=config.get("min", 0))
            config["max"] = st.number_input("Valor máximo", value=config.get("max", 100))
            config["meta"] = st.number_input("Meta", value=config.get("meta", 80))
            config["cor"] = st.color_picker("Cor do indicador", value=config.get("cor", "#4a7cf7"))

        elif tipo in ("treemap", "sunburst"):
            config["coluna_valores"] = st.text_input("Coluna de valores", value=config.get("coluna_valores", ""))
            for i in range(4):
                label = f"nivel_{i+1}"
                config[label] = st.text_input(f"Nível {i+1} (opcional)", value=config.get(label, ""),
                                              key=f"hier_{label}")
            config["escala"] = st.selectbox("Escala de cores", ["Viridis", "Plasma", "Inferno", "Magma", "Blues", "Reds"],
                                            index=["Viridis", "Plasma", "Inferno", "Magma", "Blues", "Reds"].index(config.get("escala", "Viridis")))

        elif tipo == "waterfall":
            config["coluna_x"] = st.text_input("Coluna X (categorias)", value=config.get("coluna_x", ""))
            config["coluna_y"] = st.text_input("Coluna Y (valores)", value=config.get("coluna_y", ""))

        elif tipo == "map":
            config["coluna_lat"] = st.text_input("Coluna de latitude", value=config.get("coluna_lat", ""))
            config["coluna_lon"] = st.text_input("Coluna de longitude", value=config.get("coluna_lon", ""))
            config["coluna_cor"] = st.text_input("Cor por (opcional)", value=config.get("coluna_cor", ""))
            config["coluna_tamanho"] = st.text_input("Tamanho por (opcional)", value=config.get("coluna_tamanho", ""))
            config["zoom"] = st.slider("Zoom inicial", 1, 18, value=config.get("zoom", 4))

        elif tipo == "table":
            config["colunas"] = [c.strip() for c in st.text_input("Colunas (separadas por vírgula)",
                                value=",".join(config.get("colunas", []))).split(",") if c.strip()]
            config["max_rows"] = st.number_input("Máximo de linhas", value=config.get("max_rows", 100))

    return {"tipo": tipo, "titulo": titulo, "config": config}
