import streamlit as st
import pandas as pd
import json

OPENAI_AVAILABLE = False
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    pass

def get_openai_client():
    api_key = st.secrets.get("openai_api_key", "")
    if api_key and OPENAI_AVAILABLE:
        return OpenAI(api_key=api_key)
    return None

def gerar_sql(pergunta: str, contexto: str = "") -> str:
    client = get_openai_client()
    if not client:
        return _gerar_sql_simples(pergunta)

    prompt = f"""Você é um assistente que gera consultas SQL para um banco PostgreSQL.
Contexto das tabelas disponíveis:
{contexto}

Gere APENAS o SQL, sem explicações.
Pergunta do usuário: {pergunta}"""

    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.1
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return _gerar_sql_simples(pergunta)

def _gerar_sql_simples(pergunta: str) -> str:
    pergunta_lower = pergunta.lower()
    
    if "venda" in pergunta_lower or "vendeu" in pergunta_lower:
        return "SELECT mes, SUM(vendas) as total FROM dados_demo GROUP BY mes ORDER BY mes"
    elif "produto" in pergunta_lower:
        return "SELECT produto, SUM(vendas) as total FROM dados_demo GROUP BY produto ORDER BY total DESC"
    elif "vendedor" in pergunta_lower:
        return "SELECT vendedor, SUM(vendas) as total FROM dados_demo GROUP BY vendedor ORDER BY total DESC"
    elif "regiao" in pergunta_lower:
        return "SELECT regiao, SUM(vendas) as total FROM dados_demo GROUP BY regiao ORDER BY total DESC"
    elif "meta" in pergunta_lower:
        return "SELECT mes, SUM(vendas) as vendas, SUM(meta) as meta FROM dados_demo GROUP BY mes ORDER BY mes"
    elif "compar" in pergunta_lower:
        return "SELECT mes, SUM(vendas) as vendas FROM dados_demo GROUP BY mes ORDER BY mes"
    return "SELECT * FROM dados_demo LIMIT 20"

def executar_sql(sql: str) -> pd.DataFrame:
    import numpy as np
    meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    dados_demo = pd.DataFrame({
        "mes": meses,
        "vendas": np.random.randint(10000, 50000, 12),
        "meta": np.random.randint(15000, 45000, 12),
        "custo": np.random.randint(5000, 20000, 12),
        "produto": np.random.choice(["Arroz", "Feijão", "Óleo", "Açúcar", "Café"], 12),
        "regiao": np.random.choice(["Norte", "Sul", "Leste", "Oeste"], 12),
        "vendedor": np.random.choice(["João", "Maria", "Carlos"], 12)
    })
    return dados_demo

def responder_pergunta(pergunta: str, dados: pd.DataFrame) -> str:
    client = get_openai_client()
    if client:
        dados_resumo = dados.head(20).to_json(orient="records") if not dados.empty else "{}"
        prompt = f"""Com base nos dados abaixo, responda à pergunta do usuário de forma clara e objetiva.
Dados: {dados_resumo}
Pergunta: {pergunta}
Resposta:"""
        try:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            pass

    if not dados.empty:
        total = dados.iloc[:, 1].sum() if len(dados.columns) > 1 else len(dados)
        return f"Com base nos dados, o total é {total:,.0f}. Consulte os gráficos para mais detalhes."
    return "Não foi possível processar sua pergunta com os dados disponíveis."

from modules.i18n import t

def chat_ia_screen():
    st.markdown(f"""
        <h1 style="color:#e8edf5">{t('ia.titulo')}</h1>
        <p style="color:#6b7fa3">{t('ia.subtitulo')}</p>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "dados" in msg and not msg["dados"].empty:
                st.dataframe(msg["dados"].head(10), use_container_width=True)

    pergunta = st.chat_input("Faça uma pergunta sobre seus dados...")

    if pergunta:
        st.session_state.chat_history.append({"role": "user", "content": pergunta})

        with st.chat_message("user"):
            st.markdown(pergunta)

        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                contexto = "Tabela dados_demo: mes, vendas, meta, custo, produto, regiao, vendedor"
                sql = gerar_sql(pergunta, contexto)
                dados = executar_sql(sql)
                resposta = responder_pergunta(pergunta, dados)

                st.markdown(resposta)

                if not dados.empty:
                    tab_graf, tab_tab = st.tabs(["Gráfico", "Tabela"])
                    with tab_graf:
                        import plotly.express as px
                        num_cols = dados.select_dtypes(include="number").columns
                        if len(num_cols) >= 1 and len(dados.columns) >= 2:
                            cat_col = [c for c in dados.columns if c not in num_cols]
                            if cat_col:
                                fig = px.bar(dados, x=cat_col[0], y=num_cols[0],
                                             title=pergunta[:50],
                                             color_discrete_sequence=["#4a7cf7"])
                                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                                  font=dict(color="#e8edf5"))
                                st.plotly_chart(fig, use_container_width=True)
                        with tab_tab:
                            st.dataframe(dados, use_container_width=True)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": resposta,
            "dados": dados
        })

    if len(st.session_state.chat_history) > 0 and st.button("🧹 Limpar conversa"):
        st.session_state.chat_history = []
        st.rerun()
