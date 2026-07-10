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
        elif tipo == "gantt":
            render_gantt(titulo, dados, config)
        elif tipo == "treemap":
            render_treemap(titulo, dados, config)
        elif tipo == "sunburst":
            render_sunburst(titulo, dados, config)
        elif tipo == "waterfall":
            render_waterfall(titulo, dados, config)
        elif tipo == "map":
            render_map(titulo, dados, config)
        elif tipo == "map_choropleth":
            render_map_choropleth(titulo, dados, config)
        elif tipo == "map_density":
            render_map_density(titulo, dados, config)
        elif tipo == "map_routes":
            render_map_routes(titulo, dados, config)
        elif tipo == "table":
            render_table(titulo, dados, config)
        elif tipo == "metric":
            render_metric(titulo, dados, config)
        elif tipo == "donut":
            render_donut(titulo, dados, config)
        elif tipo == "semaforo":
            render_semaforo(titulo, dados, config)
        elif tipo in ("dropdown", "list", "input", "advanced_filter", "slider",
                      "checkbox", "radio", "predefined_filter", "period",
                      "data_control", "dimension_control", "button",
                      "separator", "text_area", "image_area"):
            render_control_widget(tipo, titulo, dados, config)

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

def render_gantt(titulo, dados, config):
    col_tarefa = config.get("coluna_tarefa")
    col_inicio = config.get("coluna_inicio")
    col_fim = config.get("coluna_fim")
    col_grupo = config.get("coluna_grupo")
    col_completude = config.get("coluna_completude")

    if not col_tarefa or not col_inicio or not col_fim:
        st.info(f"Configure tarefa, início e fim para '{titulo}'")
        return

    for c in [col_tarefa, col_inicio, col_fim, col_grupo, col_completude]:
        if c and c not in dados.columns:
            st.info(f"Coluna '{c}' não encontrada em '{titulo}'")
            return

    df = dados.copy()

    # Converter datas
    for c in [col_inicio, col_fim]:
        if not pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = pd.to_datetime(df[c], errors="coerce")

    df = df.dropna(subset=[col_inicio, col_fim])

    # Ordenar por data de início
    df = df.sort_values(col_inicio)

    cores_grupo = None
    if col_grupo:
        grupos = df[col_grupo].unique()
        cor_map = {g: PALETA[i % len(PALETA)] for i, g in enumerate(grupos)}
        cores_grupo = df[col_grupo].map(cor_map).tolist()

    fig = go.Figure()

    for idx, row in df.iterrows():
        cor = cores_grupo[idx] if cores_grupo else PALETA[idx % len(PALETA)]
        label = row[col_tarefa]
        inicio = row[col_inicio]
        fim = row[col_fim]

        fig.add_trace(go.Bar(
            x=[(fim - inicio).total_seconds() * 1000],
            y=[label],
            orientation="h",
            base=[inicio],
            marker=dict(color=cor, line=dict(color="rgba(0,0,0,0.3)", width=1)),
            width=0.6,
            name=str(row[col_grupo]) if col_grupo else label,
            legendgroup=str(row[col_grupo]) if col_grupo else None,
            showlegend=False,
            hovertemplate=(
                f"<b>{label}</b><br>"
                f"Início: %{{base|%d/%m/%Y}}<br>"
                f"Fim: %{{x|%d/%m/%Y}}<br>"
                f"Duração: %{{x}}" +
                (f"<br>{col_grupo}: {row[col_grupo]}" if col_grupo else "") +
                "<extra></extra>"
            ),
        ))

        if col_completude and col_completude in df.columns:
            pct = row[col_completude]
            fig.add_annotation(
                x=fim, y=label,
                text=f"{pct:.0f}%" if pd.notna(pct) else "",
                showarrow=False,
                xanchor="left", xshift=4,
                font=dict(size=9, color="rgba(255,255,255,0.6)"),
            )

    # Hoje
    hoje = pd.Timestamp.now()
    fig.add_vline(x=hoje, line_dash="dash", line_color="rgba(255,80,80,0.5)",
                  annotation_text=" Hoje", annotation_position="top right",
                  annotation_font_size=10, annotation_font_color="rgba(255,80,80,0.7)")

    fig.update_layout(
        barmode="overlay",
        title=dict(text=titulo, font=dict(size=14, color="#8899b8")),
        xaxis=dict(
            type="date",
            title="",
            tickformat="%d/%m",
            showgrid=True, gridcolor="rgba(255,255,255,0.05)",
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            tickfont=dict(size=11),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf5"),
        margin=dict(l=10, r=60, t=30, b=10),
        height=max(200, 30 * len(df)),
        hovermode="y unified",
        bargap=0.15,
    )
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
    animacao = config.get("coluna_animacao")
    if not lat or not lon:
        st.info(f"Configure colunas de latitude/longitude para '{titulo}'")
        return
    if lat not in dados.columns or lon not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return
    fig = px.scatter_mapbox(dados, lat=lat, lon=lon,
                            color=cor if cor in dados.columns else None,
                            size=tamanho if tamanho in dados.columns else None,
                            animation_frame=animacao if animacao in dados.columns else None,
                            title=titulo, zoom=config.get("zoom", 4),
                            mapbox_style=config.get("estilo", "carto-positron"),
                            color_continuous_scale=config.get("escala", "Viridis"),
                            opacity=config.get("opacidade", 0.7),
                            hover_name=config.get("coluna_hover") if config.get("coluna_hover") in dados.columns else None)
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), font=dict(color="#e8edf5"))
    st.plotly_chart(fig, use_container_width=True)

def render_map_choropleth(titulo, dados, config):
    loc = config.get("coluna_localizacao")
    cor = config.get("coluna_cor")
    if not loc or loc not in dados.columns:
        st.info(f"Configure a coluna de localização (sigla do país/estado)")
        return
    df = dados.copy()
    fig = px.choropleth(df, locations=loc,
                        color=cor if cor in dados.columns else None,
                        title=titulo,
                        locationmode=config.get("modo", "country names"),
                        color_continuous_scale=config.get("escala", "Viridis"),
                        hover_name=config.get("coluna_hover") if config.get("coluna_hover") in dados.columns else None)
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), font=dict(color="#e8edf5"),
                      geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="#1a2340"))
    st.plotly_chart(fig, use_container_width=True)

def render_map_density(titulo, dados, config):
    lat = config.get("coluna_lat")
    lon = config.get("coluna_lon")
    if not lat or not lon:
        st.info(f"Configure colunas de latitude/longitude")
        return
    if lat not in dados.columns or lon not in dados.columns:
        st.info(f"Colunas não encontradas")
        return
    fig = px.density_mapbox(dados, lat=lat, lon=lon,
                            z=config.get("coluna_z") if config.get("coluna_z") in dados.columns else None,
                            radius=config.get("raio", 15),
                            title=titulo, zoom=config.get("zoom", 4),
                            mapbox_style=config.get("estilo", "carto-positron"),
                            color_continuous_scale=config.get("escala", "Viridis"),
                            hover_name=config.get("coluna_hover") if config.get("coluna_hover") in dados.columns else None)
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), font=dict(color="#e8edf5"))
    st.plotly_chart(fig, use_container_width=True)

def render_map_routes(titulo, dados, config):
    lat_i = config.get("coluna_lat_origem")
    lon_i = config.get("coluna_lon_origem")
    lat_f = config.get("coluna_lat_destino")
    lon_f = config.get("coluna_lon_destino")
    if not all([lat_i, lon_i, lat_f, lon_f]):
        st.info("Configure colunas de origem (lat/lon) e destino (lat/lon)")
        return
    cols = [lat_i, lon_i, lat_f, lon_f]
    if not all(c in dados.columns for c in cols):
        st.info("Colunas não encontradas")
        return
    fig = go.Figure()
    for _, row in dados.iterrows():
        fig.add_trace(go.Scattermapbox(
            mode="lines+markers",
            lon=[row[lon_i], row[lon_f]],
            lat=[row[lat_i], row[lat_f]],
            marker=dict(size=6, color=config.get("cor", "#4a7cf7")),
            line=dict(width=2, color=config.get("cor_linha", "#6b7fa3")),
            name=row.get(config.get("coluna_nome"), f"Rota {_}")
        ))
    fig.update_layout(
        mapbox=dict(style=config.get("estilo", "carto-positron"),
                    center=dict(lat=dados[lat_i].mean(), lon=dados[lon_i].mean()),
                    zoom=config.get("zoom", 4)),
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(color="#e8edf5"),
        title=dict(text=titulo, font=dict(size=14, color="#8899b8"))
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

def render_donut(titulo, dados, config):
    nomes = config.get("coluna_nomes")
    valores = config.get("coluna_valores")
    if not nomes or not valores:
        st.info(f"Configure colunas para '{titulo}'")
        return
    if nomes not in dados.columns or valores not in dados.columns:
        st.info(f"Colunas não encontradas em '{titulo}'")
        return
    fig = px.pie(dados, names=nomes, values=valores, title=titulo,
                 color_discrete_sequence=PALETA, hole=0.5)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8edf5"),
                      margin=dict(l=10, r=10, t=30, b=10),
                      annotations=[dict(text=titulo, font_size=14, showarrow=False,
                                        x=0.5, y=0.5)])
    st.plotly_chart(fig, use_container_width=True)

def render_semaforo(titulo, dados, config):
    col_valor = config.get("coluna_valor")
    col_meta = config.get("coluna_meta", "")
    lim_verde = config.get("limite_verde", 80)
    lim_amarelo = config.get("limite_amarelo", 50)

    if not col_valor or col_valor not in dados.columns:
        st.info(f"Configure coluna de valor para '{titulo}'")
        return

    valor = dados[col_valor].sum()
    meta = dados[col_meta].sum() if col_meta and col_meta in dados.columns else lim_verde

    pct = (valor / meta * 100) if meta > 0 else 0
    if pct >= lim_verde:
        cor, label, icone = "#2ecc71", "OK", "🟢"
    elif pct >= lim_amarelo:
        cor, label, icone = "#f0c040", "Atenção", "🟡"
    else:
        cor, label, icone = "#e63946", "Crítico", "🔴"

    st.markdown(f"""
        <div style="text-align:center;padding:1rem">
            <div style="font-size:3rem;line-height:1">{icone}</div>
            <div style="font-size:1.2rem;font-weight:600;color:{cor};margin:0.25rem 0">{label}</div>
            <div style="font-size:0.8rem;color:#6b7fa3">{titulo}</div>
            <div style="font-size:1.8rem;font-weight:700;color:#e8edf5">{pct:.1f}%</div>
            <div style="margin-top:0.5rem;height:6px;background:#2a3450;border-radius:3px;overflow:hidden">
                <div style="height:100%;width:{min(pct,100)}%;background:{cor};border-radius:3px;transition:width 0.5s"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#6b7fa3;margin-top:0.25rem">
                <span>0%</span>
                <span>Meta: {meta:,.0f}</span>
                <span>100%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_control_widget(tipo, titulo, dados, config):
    widget_id = str(st.session_state.get("_widget_id", id(config)))
    chave = f"cw_{widget_id}"

    # Obtain unique key from parent widget id if available
    if hasattr(st, "_widget_key_counter"):
        chave = f"cw_{st._widget_key_counter}"
    try:
        chave = f"cw_{id(config)}_{tipo}"
    except:
        pass

    if tipo == "dropdown":
        coluna = config.get("coluna", "")
        opcoes = config.get("opcoes", [])
        if coluna and coluna in dados.columns:
            opcoes = sorted(dados[coluna].unique().tolist())
        if opcoes:
            st.selectbox(titulo, [""] + opcoes, key=chave)
        else:
            st.info(f"Configure opções ou coluna para '{titulo}'")

    elif tipo == "list":
        coluna = config.get("coluna", "")
        opcoes = config.get("opcoes", [])
        if coluna and coluna in dados.columns:
            opcoes = sorted(dados[coluna].unique().tolist())
        altura = config.get("altura", 150)
        if opcoes:
            st.multiselect(titulo, opcoes, default=config.get("padrao", []), key=chave)
        else:
            st.info(f"Configure opções para '{titulo}'")

    elif tipo == "input":
        st.text_input(titulo, placeholder=config.get("placeholder", "Digite..."), key=chave)

    elif tipo == "advanced_filter":
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input(titulo, placeholder=config.get("placeholder", "Filtrar..."), key=chave)
        with col2:
            op = config.get("operador", "contém")
            st.selectbox("", ["contém", "=", ">", "<", "entre"], label_visibility="collapsed",
                         key=f"{chave}_op")

    elif tipo == "slider":
        minimo = config.get("min", 0)
        maximo = config.get("max", 100)
        passo = config.get("passo", 1)
        coluna = config.get("coluna", "")
        if coluna and coluna in dados.columns:
            minimo = float(dados[coluna].min())
            maximo = float(dados[coluna].max())
        st.slider(titulo, min_value=float(minimo), max_value=float(maximo),
                  value=(float(minimo), float(maximo)), step=float(passo), key=chave)

    elif tipo == "checkbox":
        padrao = config.get("padrao", False)
        st.checkbox(titulo, value=padrao, key=chave)

    elif tipo == "radio":
        opcoes = config.get("opcoes", [])
        coluna = config.get("coluna", "")
        if coluna and coluna in dados.columns:
            opcoes = sorted(dados[coluna].unique().tolist())
        orient = "horizontal" if config.get("orientacao_h") else "vertical"
        if opcoes:
            st.radio(titulo, opcoes, horizontal=(orient == "horizontal"), key=chave)
        else:
            st.info(f"Configure opções para '{titulo}'")

    elif tipo == "predefined_filter":
        opcoes = config.get("opcoes", ["Últimos 7 dias", "Últimos 30 dias", "Este mês",
                                        "Mês passado", "Este trimestre", "Este ano"])
        st.selectbox(titulo, opcoes, key=chave)

    elif tipo == "period":
        c1, c2 = st.columns(2)
        with c1:
            st.date_input("Início", key=f"{chave}_ini")
        with c2:
            st.date_input("Fim", key=f"{chave}_fim")

    elif tipo == "data_control":
        col_base = config.get("coluna_base", "")
        colunas = [c for c in dados.columns if c] if not dados.empty else []
        if colunas:
            st.selectbox(titulo, colunas, index=colunas.index(col_base) if col_base in colunas else 0,
                         key=chave)
        else:
            st.info("Sem dados disponíveis")

    elif tipo == "dimension_control":
        colunas_disc = [c for c in dados.columns if c and not pd.api.types.is_numeric_dtype(dados[c])] if not dados.empty else []
        if colunas_disc:
            st.selectbox(titulo, colunas_disc, key=chave)
        else:
            st.info("Nenhuma dimensão categórica encontrada")

    elif tipo == "button":
        rotulo = config.get("rotulo", "Executar")
        variante = config.get("variante", "primary")
        if st.button(rotulo, type=variante, use_container_width=True, key=chave):
            if config.get("acao", ""):
                st.info(f"Ação: {config['acao']}")

    elif tipo == "separator":
        espessura = config.get("espessura", 1)
        cor_sep = config.get("cor", "#2a3450")
        margem = config.get("margem", 12)
        st.markdown(f"""
            <hr style="border:none;border-top:{espessura}px solid {cor_sep};
                       margin:{margem}px 0;border-radius:2px">
        """, unsafe_allow_html=True)

    elif tipo == "text_area":
        st.markdown(f"""
            <div style="padding:0.5rem;border-radius:8px;border:1px solid #2a3450;
                        background:#1a2340;min-height:60px">
                <div style="font-size:0.85rem;color:#8899b8;margin-bottom:0.25rem">{titulo}</div>
                <div style="color:#e8edf5;font-size:0.9rem;line-height:1.5;white-space:pre-wrap">
                    {config.get("conteudo", "")}
                </div>
            </div>
        """, unsafe_allow_html=True)

    elif tipo == "image_area":
        url = config.get("url", "")
        alt = config.get("alt", titulo)
        if url:
            st.markdown(f"""
                <div style="text-align:center;padding:0.5rem">
                    <img src="{url}" alt="{alt}"
                         style="max-width:100%;border-radius:8px;border:1px solid #2a3450">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"Configure URL da imagem para '{titulo}'")

# SVG previews for each chart type
_CHART_ICONS = {
    "kpi": "📊", "metric": "📐", "bar": "📊", "line": "📈", "area": "📉",
    "pie": "🥧", "scatter": "⬤", "histogram": "📊", "heatmap": "🟥",
    "funnel": "🔻", "gauge": "🎯", "treemap": "🧩", "sunburst": "✴️",
    "waterfall": "📊", "map": "🗺️", "map_choropleth": "🗺️", "map_density": "🌐",
    "map_routes": "🗺️", "table": "🗂️", "gantt": "⏳", "donut": "⭕", "semaforo": "🔴",
}

_CONTROL_ICONS = {
    "dropdown": "📋", "list": "📜", "input": "✏️", "advanced_filter": "🔍",
    "slider": "🎚️", "checkbox": "✅", "radio": "⚪", "predefined_filter": "📌",
    "period": "📅", "data_control": "🗃️", "dimension_control": "📐", "button": "🔘",
    "separator": "➖", "text_area": "📝", "image_area": "🖼️",
}

_CATEGORIAS = [
    {
        "nome": "📊 KPIs & Métricas",
        "tipos": [
            ("kpi", "KPI"),
            ("metric", "Métrica"),
        ]
    },
    {
        "nome": "📊 Barras",
        "tipos": [
            ("bar", "Barras"),
        ]
    },
    {
        "nome": "📈 Linhas & Área",
        "tipos": [
            ("line", "Linha"),
            ("area", "Área"),
        ]
    },
    {
        "nome": "🥧 Pizza & Composição",
        "tipos": [
            ("pie", "Pizza"),
            ("donut", "Donut"),
            ("funnel", "Funil"),
            ("treemap", "Treemap"),
            ("sunburst", "Sunburst"),
        ]
    },
    {
        "nome": "✦ Distribuição & Correlação",
        "tipos": [
            ("scatter", "Dispersão"),
            ("histogram", "Histograma"),
            ("heatmap", "Mapa de Calor"),
            ("waterfall", "Waterfall"),
        ]
    },
    {
        "nome": "⏱ Indicadores & Planejamento",
        "tipos": [
            ("gauge", "Gauge"),
            ("semaforo", "Semáforo"),
            ("gantt", "Gantt"),
        ]
    },
    {
        "nome": "🗺️ Geográficos",
        "tipos": [
            ("map", "Mapa de Pontos"),
            ("map_choropleth", "Coroplético"),
            ("map_density", "Densidade"),
            ("map_routes", "Rotas"),
        ]
    },
    {
        "nome": "📋 Tabelas",
        "tipos": [
            ("table", "Tabela"),
        ]
    },
    {
        "nome": "🔧 Controles & Filtros",
        "tipos": [
            ("dropdown", "Lista Suspensa"),
            ("list", "Lista Fixa"),
            ("input", "Caixa de Entrada"),
            ("advanced_filter", "Filtro Avançado"),
            ("slider", "Controle Deslizante"),
            ("checkbox", "Caixa de Seleção"),
            ("radio", "Radio Button"),
            ("predefined_filter", "Filtro Pré-definido"),
            ("period", "Controle de Período"),
            ("data_control", "Controle de Dados"),
            ("dimension_control", "Controle de Dimensão"),
            ("button", "Botão"),
        ]
    },
    {
        "nome": "📝 Conteúdo",
        "tipos": [
            ("separator", "Separador"),
            ("text_area", "Área de Texto"),
            ("image_area", "Área de Imagem"),
        ]
    },
]

def editor_widget(widget_data: dict = None) -> dict:
    from modules.themes import get_cores
    cores = get_cores()

    tipo_selecionado = st.session_state.get("widget_tipo_selecionado")
    if widget_data and not tipo_selecionado:
        tipo_selecionado = widget_data.get("tipo", "kpi")
        st.session_state.widget_tipo_selecionado = tipo_selecionado

    st.markdown("### ⚙️ Selecione o tipo de gráfico")

    # CSS dinâmico para destacar o botão ativo
    tipo_ativo = st.session_state.get("widget_tipo_selecionado", "")
    if tipo_ativo:
        st.markdown(f"""
        <style>
            button[key="chart_{tipo_ativo}"] {{
                border-color: {cores["accent"]} !important;
                background: color-mix(in srgb, {cores["accent"]} 12%, transparent) !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }}
        </style>
        """, unsafe_allow_html=True)

    for cat in _CATEGORIAS:
        st.markdown(f"""
            <div style="font-size:0.75rem;font-weight:600;color:{cores['text_secondary']};
                        text-transform:uppercase;letter-spacing:0.06em;
                        margin:1rem 0 0.5rem 0;padding-bottom:0.25rem;
                        border-bottom:1px solid {cores['border']}">
                {cat['nome']}
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(len(cat["tipos"]))
        for idx, (tipo_key, tipo_nome) in enumerate(cat["tipos"]):
            with cols[idx]:
                is_active = st.session_state.get("widget_tipo_selecionado") == tipo_key
                icone = _CHART_ICONS.get(tipo_key) or _CONTROL_ICONS.get(tipo_key, "")
                btn_label = f"{icone}\n{tipo_nome}"
                if st.button(btn_label, key=f"chart_{tipo_key}", use_container_width=True):
                    st.session_state.widget_tipo_selecionado = tipo_key
                    st.rerun()

    if not tipo_selecionado:
        st.info("👆 Clique em um tipo de gráfico acima para configurá-lo")
        return {}

    tipo = tipo_selecionado

    st.markdown("---")
    st.markdown(f"### ⚙️ Configurar: {dict(sum([cat['tipos'] for cat in _CATEGORIAS], [])).get(tipo, tipo)}")

    titulo = st.text_input("Título do widget",
                           value=widget_data.get("titulo", "") if widget_data else "",
                           placeholder="Ex: Vendas por mês")

    config = {}
    if widget_data and isinstance(widget_data.get("config"), dict):
        config = widget_data["config"]

    if tipo in ("kpi", "metric"):
        config["coluna_valor"] = st.text_input("Coluna de valor", value=config.get("coluna_valor", ""))
        if tipo == "kpi":
            config["coluna_meta"] = st.text_input("Coluna de meta (opcional)", value=config.get("coluna_meta", ""))
        else:
            config["coluna_categoria"] = st.text_input("Coluna de categoria", value=config.get("coluna_categoria", ""))
        config["prefixo"] = st.text_input("Prefixo (ex: R$)", value=config.get("prefixo", ""))
        config["sufixo"] = st.text_input("Sufixo (ex: %)", value=config.get("sufixo", ""))

    elif tipo == "bar":
        config["coluna_x"] = st.text_input("Coluna X (categoria)", value=config.get("coluna_x", ""))
        config["coluna_y"] = st.text_input("Coluna Y (valor)", value=config.get("coluna_y", ""))
        config["coluna_agrupar"] = st.text_input("Agrupar por (opcional)", value=config.get("coluna_agrupar", ""))
        config["cor"] = st.color_picker("Cor", value=config.get("cor", "#4a7cf7"))
        config["orientacao"] = st.radio("Orientação", ["v", "h"], horizontal=True)
        config["empilhar"] = st.checkbox("Empilhar grupos", value=config.get("empilhar", False))

    elif tipo == "line":
        config["coluna_x"] = st.text_input("Coluna X (categoria)", value=config.get("coluna_x", ""))
        config["coluna_y"] = st.text_input("Coluna Y (valor)", value=config.get("coluna_y", ""))
        config["coluna_agrupar"] = st.text_input("Agrupar por (opcional)", value=config.get("coluna_agrupar", ""))
        config["cor"] = st.color_picker("Cor", value=config.get("cor", "#4a7cf7"))

    elif tipo == "area":
        config["coluna_x"] = st.text_input("Coluna X (categoria)", value=config.get("coluna_x", ""))
        config["coluna_y"] = st.text_input("Coluna Y (valor)", value=config.get("coluna_y", ""))
        config["coluna_agrupar"] = st.text_input("Agrupar por (opcional)", value=config.get("coluna_agrupar", ""))
        config["cor"] = st.color_picker("Cor", value=config.get("cor", "#4a7cf7"))

    elif tipo == "pie":
        config["coluna_nomes"] = st.text_input("Coluna de categorias", value=config.get("coluna_nomes", ""))
        config["coluna_valores"] = st.text_input("Coluna de valores", value=config.get("coluna_valores", ""))

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

    elif tipo == "gantt":
        config["coluna_tarefa"] = st.text_input("Coluna com nome da tarefa", value=config.get("coluna_tarefa", ""),
            help="Ex: nome da atividade ou etapa")
        config["coluna_inicio"] = st.text_input("Coluna com data de início", value=config.get("coluna_inicio", ""),
            help="Coluna de data (datetime ou string)")
        config["coluna_fim"] = st.text_input("Coluna com data de fim", value=config.get("coluna_fim", ""),
            help="Coluna de data (datetime ou string)")
        config["coluna_grupo"] = st.text_input("Agrupar por cor (opcional)", value=config.get("coluna_grupo", ""),
            help="Ex: responsável, departamento, fase")
        config["coluna_completude"] = st.text_input("% concluído (opcional)", value=config.get("coluna_completude", ""),
            help="Coluna numérica 0-100 para barra de progresso")

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
        config["coluna_lat"] = st.text_input("Latitude", value=config.get("coluna_lat", ""))
        config["coluna_lon"] = st.text_input("Longitude", value=config.get("coluna_lon", ""))
        config["coluna_cor"] = st.text_input("Cor por (opcional)", value=config.get("coluna_cor", ""))
        config["coluna_tamanho"] = st.text_input("Tamanho por (opcional)", value=config.get("coluna_tamanho", ""))
        config["coluna_hover"] = st.text_input("Texto ao passar mouse (opcional)", value=config.get("coluna_hover", ""))
        config["coluna_animacao"] = st.text_input("Animação (opcional)", value=config.get("coluna_animacao", ""),
            help="Coluna com ano/mês para animar o mapa")
        config["zoom"] = st.slider("Zoom inicial", 1, 18, value=config.get("zoom", 4))
        config["opacidade"] = st.slider("Opacidade dos pontos", 0.1, 1.0, value=config.get("opacidade", 0.7))
        config["estilo"] = st.selectbox("Estilo do mapa",
            ["carto-positron", "open-street-map", "stamen-terrain", "stamen-toner"],
            index=["carto-positron","open-street-map","stamen-terrain","stamen-toner"].index(config.get("estilo", "carto-positron")))

    elif tipo == "map_choropleth":
        config["coluna_localizacao"] = st.text_input("Coluna com país/estado (sigla)",
            value=config.get("coluna_localizacao", ""),
            help="Ex: BRA, USA, SP, RJ — siglas ISO")
        config["coluna_cor"] = st.text_input("Coluna de valor (cor)", value=config.get("coluna_cor", ""))
        config["coluna_hover"] = st.text_input("Texto ao passar mouse (opcional)", value=config.get("coluna_hover", ""))
        config["modo"] = st.selectbox("Modo de localização",
            ["country names", "ISO-3", "USA-states", "geojson-id"],
            index=["country names","ISO-3","USA-states","geojson-id"].index(config.get("modo", "country names")))

    elif tipo == "map_density":
        config["coluna_lat"] = st.text_input("Latitude", value=config.get("coluna_lat", ""))
        config["coluna_lon"] = st.text_input("Longitude", value=config.get("coluna_lon", ""))
        config["coluna_z"] = st.text_input("Intensidade (opcional)", value=config.get("coluna_z", ""))
        config["coluna_hover"] = st.text_input("Texto ao passar mouse (opcional)", value=config.get("coluna_hover", ""))
        config["raio"] = st.slider("Raio de densidade", 5, 50, value=config.get("raio", 15))
        config["zoom"] = st.slider("Zoom inicial", 1, 18, value=config.get("zoom", 4))

    elif tipo == "map_routes":
        config["coluna_lat_origem"] = st.text_input("Latitude (origem)", value=config.get("coluna_lat_origem", ""))
        config["coluna_lon_origem"] = st.text_input("Longitude (origem)", value=config.get("coluna_lon_origem", ""))
        config["coluna_lat_destino"] = st.text_input("Latitude (destino)", value=config.get("coluna_lat_destino", ""))
        config["coluna_lon_destino"] = st.text_input("Longitude (destino)", value=config.get("coluna_lon_destino", ""))
        config["coluna_nome"] = st.text_input("Nome da rota (opcional)", value=config.get("coluna_nome", ""))
        config["zoom"] = st.slider("Zoom inicial", 1, 18, value=config.get("zoom", 4))

    elif tipo == "donut":
        config["coluna_nomes"] = st.text_input("Coluna de categorias", value=config.get("coluna_nomes", ""))
        config["coluna_valores"] = st.text_input("Coluna de valores", value=config.get("coluna_valores", ""))

    elif tipo == "semaforo":
        config["coluna_valor"] = st.text_input("Coluna de valor", value=config.get("coluna_valor", ""))
        config["coluna_meta"] = st.text_input("Coluna de meta (opcional)", value=config.get("coluna_meta", ""))
        c1, c2 = st.columns(2)
        with c1:
            config["limite_verde"] = st.number_input("Limite verde (%)", value=config.get("limite_verde", 80), min_value=0, max_value=100)
        with c2:
            config["limite_amarelo"] = st.number_input("Limite amarelo (%)", value=config.get("limite_amarelo", 50), min_value=0, max_value=100)

    elif tipo == "dropdown":
        config["coluna"] = st.text_input("Coluna de dados", value=config.get("coluna", ""),
            help="Nome da coluna no dataset para extrair opções automaticamente")
        config["opcoes"] = [x.strip() for x in st.text_input("Opções fixas (separadas por vírgula)",
            value=",".join(config.get("opcoes", []))).split(",") if x.strip()]

    elif tipo == "list":
        config["coluna"] = st.text_input("Coluna de dados", value=config.get("coluna", ""),
            help="Nome da coluna no dataset para extrair opções")
        config["opcoes"] = [x.strip() for x in st.text_input("Opções fixas (separadas por vírgula)",
            value=",".join(config.get("opcoes", []))).split(",") if x.strip()]
        config["padrao"] = [x.strip() for x in st.text_input("Valores padrão (separados por vírgula)",
            value=",".join(config.get("padrao", []))).split(",") if x.strip()]
        config["altura"] = st.number_input("Altura (px)", value=config.get("altura", 150))

    elif tipo == "input":
        config["placeholder"] = st.text_input("Placeholder", value=config.get("placeholder", "Digite..."))

    elif tipo == "advanced_filter":
        config["placeholder"] = st.text_input("Placeholder", value=config.get("placeholder", "Filtrar..."))
        config["operador"] = st.selectbox("Operador padrão",
            ["contém", "=", ">", "<", "entre"],
            index=["contém", "=", ">", "<", "entre"].index(config.get("operador", "contém")))

    elif tipo == "slider":
        config["coluna"] = st.text_input("Coluna para limites (opcional)", value=config.get("coluna", ""),
            help="Se preenchido, usa min/max da coluna")
        c1, c2, c3 = st.columns(3)
        with c1:
            config["min"] = st.number_input("Mínimo", value=config.get("min", 0))
        with c2:
            config["max"] = st.number_input("Máximo", value=config.get("max", 100))
        with c3:
            config["passo"] = st.number_input("Passo", value=config.get("passo", 1), min_value=0.01)

    elif tipo == "checkbox":
        config["padrao"] = st.checkbox("Marcado por padrão", value=config.get("padrao", False))

    elif tipo == "radio":
        config["opcoes"] = [x.strip() for x in st.text_input("Opções (separadas por vírgula)",
            value=",".join(config.get("opcoes", []))).split(",") if x.strip()]
        config["orientacao_h"] = st.checkbox("Orientação horizontal", value=config.get("orientacao_h", False))

    elif tipo == "predefined_filter":
        config["opcoes"] = [x.strip() for x in st.text_input("Opções (separadas por vírgula)",
            value=",".join(config.get("opcoes", [
                "Últimos 7 dias", "Últimos 30 dias", "Este mês",
                "Mês passado", "Este trimestre", "Este ano"
            ]))).split(",") if x.strip()]

    elif tipo == "period":
        pass  # No additional config needed; uses date inputs directly

    elif tipo == "data_control":
        config["coluna_base"] = st.text_input("Coluna padrão", value=config.get("coluna_base", ""),
            help="Coluna selecionada por padrão")

    elif tipo == "dimension_control":
        pass  # Auto-detects categorical columns

    elif tipo == "button":
        config["rotulo"] = st.text_input("Rótulo do botão", value=config.get("rotulo", "Executar"))
        config["variante"] = st.selectbox("Variante", ["primary", "secondary"],
            index=["primary", "secondary"].index(config.get("variante", "primary")))
        config["acao"] = st.text_input("Ação ao clicar", value=config.get("acao", ""),
            placeholder="Ex: atualizar_dashboard")

    elif tipo == "separator":
        config["espessura"] = st.number_input("Espessura (px)", value=config.get("espessura", 1), min_value=1)
        config["cor"] = st.color_picker("Cor", value=config.get("cor", "#2a3450"))
        config["margem"] = st.number_input("Margem (px)", value=config.get("margem", 12), min_value=0)

    elif tipo == "text_area":
        config["conteudo"] = st.text_area("Conteúdo", value=config.get("conteudo", ""),
            placeholder="Digite o conteúdo do texto...")

    elif tipo == "image_area":
        config["url"] = st.text_input("URL da imagem", value=config.get("url", ""),
            placeholder="https://exemplo.com/imagem.png")
        config["alt"] = st.text_input("Texto alternativo", value=config.get("alt", ""),
            placeholder="Descrição da imagem")

    return {"tipo": tipo, "titulo": titulo, "config": config}
