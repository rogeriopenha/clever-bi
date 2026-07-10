import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

def sugerir_grafico(df: pd.DataFrame) -> list:
    sugestoes = []
    colunas = df.columns.tolist()
    dtypes = df.dtypes.to_dict()

    num_cols = [c for c in colunas if pd.api.types.is_numeric_dtype(dtypes[c])]
    cat_cols = [c for c in colunas if pd.api.types.is_object_dtype(dtypes[c])
                or pd.api.types.is_categorical_dtype(dtypes[c])]
    date_cols = [c for c in colunas if pd.api.types.is_datetime64_any_dtype(dtypes[c])]

    if not num_cols:
        return [{"tipo": "table", "titulo": "Visão Geral", "config": {"colunas": colunas[:10], "max_rows": 100}}]

    if len(num_cols) == 1:
        if cat_cols:
            sugestoes.append({
                "tipo": "bar", "titulo": f"{num_cols[0]} por {cat_cols[0]}",
                "config": {"coluna_x": cat_cols[0], "coluna_y": num_cols[0], "cor": "#4a7cf7"}
            })
            sugestoes.append({
                "tipo": "pie", "titulo": f"Distribuição de {num_cols[0]}",
                "config": {"coluna_nomes": cat_cols[0], "coluna_valores": num_cols[0]}
            })
        if date_cols:
            sugestoes.append({
                "tipo": "line", "titulo": f"{num_cols[0]} ao longo do tempo",
                "config": {"coluna_x": date_cols[0], "coluna_y": num_cols[0], "cor": "#4a7cf7"}
            })
        sugestoes.append({
            "tipo": "kpi", "titulo": f"Total {num_cols[0]}",
            "config": {"coluna_valor": num_cols[0], "prefixo": "", "sufixo": ""}
        })

    elif len(num_cols) >= 2:
        if date_cols:
            sugestoes.append({
                "tipo": "line", "titulo": f"{num_cols[0]} e {num_cols[1]} ao longo do tempo",
                "config": {"coluna_x": date_cols[0], "coluna_y": num_cols[0], "cor": "#4a7cf7"}
            })
        if cat_cols:
            sugestoes.append({
                "tipo": "bar", "titulo": f"{num_cols[0]} por {cat_cols[0]}",
                "config": {"coluna_x": cat_cols[0], "coluna_y": num_cols[0], "cor": "#4a7cf7"}
            })
            if len(cat_cols) >= 2:
                sugestoes.append({
                    "tipo": "treemap", "titulo": f"Hierarquia de {num_cols[0]}",
                    "config": {"coluna_valores": num_cols[0], "nivel_1": cat_cols[0], "nivel_2": cat_cols[1]}
                })
        sugestoes.append({
            "tipo": "scatter", "titulo": f"{num_cols[0]} vs {num_cols[1]}",
            "config": {"coluna_x": num_cols[0], "coluna_y": num_cols[1],
                       "coluna_cor": cat_cols[0] if cat_cols else ""}
        })

    if len(num_cols) >= 3 and cat_cols:
        sugestoes.append({
            "tipo": "heatmap", "titulo": f"Correlação: {cat_cols[0]} vs {num_cols[0]}",
            "config": {"coluna_x": cat_cols[0], "coluna_y": num_cols[0], "coluna_z": num_cols[1]}
        })

    if not sugestoes:
        sugestoes.append({
            "tipo": "table", "titulo": "Dados",
            "config": {"colunas": colunas[:10], "max_rows": 100}
        })

    return sugestoes[:5]


def gerar_insights(df: pd.DataFrame) -> list:
    insights = []
    colunas = df.columns.tolist()
    dtypes = df.dtypes.to_dict()
    num_cols = [c for c in colunas if pd.api.types.is_numeric_dtype(dtypes[c])]
    cat_cols = [c for c in colunas if pd.api.types.is_object_dtype(dtypes[c])
                or pd.api.types.is_categorical_dtype(dtypes[c])]
    date_cols = [c for c in colunas if pd.api.types.is_datetime64_any_dtype(dtypes[c])]

    # Tamanho
    insights.append(f"📊 A base contém **{len(df):,}** registros e **{len(colunas)}** colunas.")

    # Nulos
    nulos = df.isnull().sum()
    col_com_nulos = nulos[nulos > 0]
    if not col_com_nulos.empty:
        for c, v in col_com_nulos.items():
            pct = v / len(df) * 100
            insights.append(f"⚠️ Coluna **{c}** tem **{v:,}** valores nulos ({pct:.1f}%).")

    # Numéricas - estatísticas
    if num_cols:
        for c in num_cols[:3]:
            serie = df[c].dropna()
            if len(serie) > 0:
                insights.append(f"📈 **{c}**: média {serie.mean():,.1f}, "
                               f"mín {serie.min():,.0f}, máx {serie.max():,.0f}, "
                               f"total {serie.sum():,.0f}")

    # Categóricas - frequência
    if cat_cols:
        for c in cat_cols[:2]:
            top = df[c].value_counts().head(3)
            tops = ", ".join([f"{k} ({v})" for k, v in top.items()])
            insights.append(f"🏷️ **{c}**: principais valores = {tops}")

    # Datas - período
    if date_cols:
        for c in date_cols[:1]:
            serie = df[c].dropna()
            if len(serie) > 0:
                insights.append(f"📅 **{c}**: de {serie.min().strftime('%d/%m/%Y')} "
                               f"a {serie.max().strftime('%d/%m/%Y')} "
                               f"({(serie.max() - serie.min()).days} dias)")

    # Correlação forte
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        for i in range(len(num_cols)):
            for j in range(i+1, len(num_cols)):
                v = corr.iloc[i, j]
                if abs(v) > 0.7:
                    direcao = "positiva" if v > 0 else "negativa"
                    insights.append(f"🔗 Correlação **{direcao}** forte ({v:.2f}) entre **{num_cols[i]}** e **{num_cols[j]}**")

    return insights


def profiler_qualidade(df: pd.DataFrame) -> dict:
    profile = {
        "registros": len(df),
        "colunas": len(df.columns),
        "memoria_kb": df.memory_usage(deep=True).sum() / 1024,
        "duplicatas": df.duplicated().sum(),
        "colunas_info": []
    }

    for col in df.columns:
        info = {"nome": col,
                "tipo": str(df[col].dtype),
                "nulos": int(df[col].isnull().sum()),
                "nulos_pct": round(df[col].isnull().sum() / len(df) * 100, 1) if len(df) > 0 else 0,
                "unicos": int(df[col].nunique())}
        if pd.api.types.is_numeric_dtype(df[col]):
            info.update({
                "media": round(df[col].mean(), 2) if not df[col].isnull().all() else None,
                "min": round(df[col].min(), 2) if not df[col].isnull().all() else None,
                "max": round(df[col].max(), 2) if not df[col].isnull().all() else None,
                "std": round(df[col].std(), 2) if not df[col].isnull().all() else None,
            })
        profile["colunas_info"].append(info)

    return profile


def gerar_previsao(df: pd.DataFrame, coluna_data: str, coluna_valor: str, periodos: int = 12) -> pd.DataFrame:
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
    except ImportError:
        return _previsao_simples(df, coluna_data, coluna_valor, periodos)

    if coluna_data not in df.columns or coluna_valor not in df.columns:
        return pd.DataFrame()

    ts = df[[coluna_data, coluna_valor]].copy()
    ts[coluna_data] = pd.to_datetime(ts[coluna_data])
    ts = ts.sort_values(coluna_data).set_index(coluna_data)
    ts = ts.resample("ME").sum()

    if len(ts) < 6:
        return _previsao_simples(df, coluna_data, coluna_valor, periodos)

    try:
        model = ExponentialSmoothing(
            ts[coluna_valor].fillna(0),
            seasonal_periods=min(12, len(ts) // 2),
            trend="add",
            seasonal="add"
        ).fit()
        forecast = model.forecast(periodos)
        ultima_data = ts.index[-1]
        datas_futuras = pd.date_range(start=ultima_data + timedelta(days=30),
                                      periods=periodos, freq="ME")
        return pd.DataFrame({
            coluna_data: list(ts.index) + list(datas_futuras),
            coluna_valor: list(ts[coluna_valor]) + list(forecast),
            "tipo": ["histórico"] * len(ts) + ["previsão"] * periodos
        })
    except:
        return _previsao_simples(df, coluna_data, coluna_valor, periodos)


def _previsao_simples(df, coluna_data, coluna_valor, periodos):
    if coluna_data not in df.columns or coluna_valor not in df.columns:
        return pd.DataFrame()
    ts = df[[coluna_data, coluna_valor]].copy()
    ts[coluna_data] = pd.to_datetime(ts[coluna_data])
    ts = ts.sort_values(coluna_data)
    if len(ts) < 3:
        return pd.DataFrame()
    from numpy import polyfit, polyval
    x = np.arange(len(ts))
    y = ts[coluna_valor].values
    z = polyfit(x, y, 1)
    fut = np.arange(len(ts), len(ts) + periodos)
    prev = polyval(z, fut)
    ultima = ts[coluna_data].iloc[-1]
    dias = (ts[coluna_data].iloc[-1] - ts[coluna_data].iloc[0]).days
    passo = max(1, dias // max(1, len(ts) - 1))
    datas_futuras = [ultima + timedelta(days=passo * (i + 1)) for i in range(periodos)]
    return pd.DataFrame({
        coluna_data: list(ts[coluna_data]) + datas_futuras,
        coluna_valor: list(y) + list(prev),
        "tipo": ["histórico"] * len(ts) + ["previsão"] * periodos
    })


def simulador_cenario(df: pd.DataFrame, coluna_valor: str, colunas_grupo: list = None) -> dict:
    if coluna_valor not in df.columns:
        return {"erro": "Coluna de valor não encontrada"}
    total_base = df[coluna_valor].sum()
    resultado = {"total_base": total_base, "cenarios": []}
    if colunas_grupo:
        for c in colunas_grupo:
            if c in df.columns:
                participacao = df.groupby(c)[coluna_valor].sum().reset_index()
                participacao["pct"] = participacao[coluna_valor] / total_base * 100
                resultado["cenarios"].append({
                    "dimensao": c,
                    "dados": participacao.to_dict("records")
                })
    return resultado


def wizard_criacao():
    st.markdown("### 🪄 Assistente Inteligente de Dashboard")
    st.markdown("Em 3 passos você cria um dashboard completo.")

    passo = st.session_state.get("wizard_passo", 1)
    cols = st.columns(3)
    for i in range(1, 4):
        with cols[i - 1]:
            status = "✅" if passo > i else ("▶️" if passo == i else "⏳")
            st.markdown(f"{status} **Passo {i}**")

    st.markdown("---")

    if passo == 1:
        st.markdown("**Passo 1: Escolha a origem dos dados**")
        from modules.data_sources import listar_datasets
        datasets = listar_datasets()
        opcoes = {"demo": "📊 Dados de demonstração"}
        if not datasets.empty:
            for _, d in datasets.iterrows():
                opcoes[d["id"]] = f"🗄️ {d['nome']}"

        origem = st.radio("Selecione a origem", list(opcoes.values()), key="wizard_origem")
        if st.button("➡️ Próximo", type="primary"):
            st.session_state.wizard_origem = origem
            st.session_state.wizard_passo = 2
            st.rerun()

    elif passo == 2:
        st.markdown("**Passo 2: Configure os gráficos**")
        st.info("Use o editor abaixo para personalizar seus widgets.")
        from modules.widgets import editor_widget
        cfg = editor_widget(st.session_state.get("wizard_widget_cfg"))
        st.session_state.wizard_widget_cfg = cfg

        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Voltar"):
                st.session_state.wizard_passo = 1
                st.rerun()
        with c2:
            if st.button("➡️ Próximo", type="primary"):
                st.session_state.wizard_passo = 3
                st.rerun()

    elif passo == 3:
        st.markdown("**Passo 3: Nomeie e crie**")
        nome_dash = st.text_input("Nome do dashboard", placeholder="Ex: Painel de Vendas")
        desc_dash = st.text_area("Descrição (opcional)", placeholder="O que este dashboard mostra?")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Voltar", use_container_width=True):
                st.session_state.wizard_passo = 2
                st.rerun()
        with col2:
            if st.button("✅ Criar Dashboard", type="primary", use_container_width=True):
                if nome_dash:
                    from modules.database import insert_record, current_user, get_tenant_id
                    tenant_id = get_tenant_id()
                    user = current_user()
                    result = insert_record("dashboards", {
                        "tenant_id": tenant_id,
                        "nome": nome_dash,
                        "descricao": desc_dash,
                        "layout": json.dumps([]),
                        "criado_por": user.get("id")
                    })
                    if "error" not in result:
                        dash_id = result.get("id") if isinstance(result, dict) else result
                        cfg = st.session_state.get("wizard_widget_cfg", {})
                        if cfg and cfg.get("titulo"):
                            from modules.dashboards import salvar_widget
                            salvar_widget(dash_id, cfg)
                        st.success(f"Dashboard '{nome_dash}' criado!")
                        st.session_state.wizard_passo = 1
                        st.session_state.wizard_widget_cfg = {}
                        st.rerun()
        with col3:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.wizard_passo = 1
                st.session_state.wizard_widget_cfg = {}
                st.rerun()
