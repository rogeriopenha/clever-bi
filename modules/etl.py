import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

def tela_etl():
    st.markdown("### 🔄 ETL — Transformação de Dados")
    st.markdown("Carregue, transforme e exporte seus dados em poucos cliques.")

    if "etl_df" not in st.session_state:
        st.session_state.etl_df = None
    if "etl_history" not in st.session_state:
        st.session_state.etl_history = []

    # Abas
    tab_entrada, tab_transform, tab_saida = st.tabs(["📥 Entrada", "⚙️ Transformações", "📤 Saída"])

    with tab_entrada:
        fonte = st.radio("Origem dos dados", ["Upload", "Colar dados", "Dataset existente", "Exemplo"])
        df = None

        if fonte == "Upload":
            arquivo = st.file_uploader("Selecione o arquivo", type=["csv", "xlsx", "xls", "json", "txt"])
            if arquivo:
                try:
                    if arquivo.name.endswith(".csv") or arquivo.name.endswith(".txt"):
                        sep = st.selectbox("Separador", [",", ";", "|", "\t"], key="etl_sep")
                        df = pd.read_csv(arquivo, sep=sep)
                    elif arquivo.name.endswith(".json"):
                        df = pd.read_json(arquivo)
                    else:
                        df = pd.read_excel(arquivo)
                except Exception as e:
                    st.error(f"Erro ao ler: {e}")

        elif fonte == "Colar dados":
            texto = st.text_area("Cole os dados (CSV/TSV)", height=150,
                                 placeholder="valor,categoria,data\n100,Vendas,2024-01-01")
            if texto:
                sep = st.selectbox("Separador", [",", ";", "|", "\t"], key="etl_sep2")
                try:
                    df = pd.read_csv(io.StringIO(texto), sep=sep)
                except Exception as e:
                    st.error(f"Erro: {e}")

        elif fonte == "Dataset existente":
            from modules.data_sources import listar_datasets
            datasets = listar_datasets()
            if not datasets.empty:
                nome_ds = st.selectbox("Selecione o dataset", datasets["nome"].tolist())
                if nome_ds:
                    ds_row = datasets[datasets["nome"] == nome_ds].iloc[0]
                    from modules.data_sources import executar_dataset
                    df = executar_dataset(ds_row["id"])
            else:
                st.info("Nenhum dataset disponível")

        elif fonte == "Exemplo":
            import numpy as np
            df = pd.DataFrame({
                "nome": ["João", "Maria", "Carlos", "Ana", "Pedro"],
                "vendas": [12000, 18000, 9500, 22000, 15000],
                "meta": [10000, 15000, 10000, 20000, 12000],
                "regiao": ["Sul", "Sudeste", "Norte", "Nordeste", "Centro-Oeste"],
                "data": pd.date_range("2024-01-01", periods=5, freq="ME")
            })

        if df is not None and not df.empty:
            st.success(f"✅ {len(df)} registros, {len(df.columns)} colunas")
            st.dataframe(df.head(20), use_container_width=True)
            if st.button("📥 Carregar para ETL", key="etl_carregar", type="primary"):
                st.session_state.etl_df = df.copy()
                st.session_state.etl_history = [("Original", df.shape)]
                st.rerun()

    with tab_transform:
        if st.session_state.etl_df is None:
            st.info("Carregue dados primeiro na aba 'Entrada'")
            return

        df = st.session_state.etl_df.copy()

        with st.expander("📊 Informações", expanded=True):
            st.markdown(f"**{len(df)}** linhas × **{len(df.columns)}** colunas")
            st.dataframe(pd.DataFrame({
                "coluna": df.columns,
                "tipo": df.dtypes.astype(str),
                "nulos": df.isnull().sum().values,
                "unicos": df.nunique().values
            }), use_container_width=True)

        with st.expander("✂️ Filtrar linhas"):
            col_filtro = st.selectbox("Coluna para filtrar", df.columns, key="etl_filtro_col")
            if pd.api.types.is_numeric_dtype(df[col_filtro]):
                mn, mx = float(df[col_filtro].min()), float(df[col_filtro].max())
                vals = st.slider("Intervalo", mn, mx, (mn, mx), key="etl_filtro_val")
                df = df[(df[col_filtro] >= vals[0]) & (df[col_filtro] <= vals[1])]
            else:
                vals = st.multiselect("Valores", df[col_filtro].unique().tolist(),
                                      default=df[col_filtro].unique().tolist(), key="etl_filtro_cat")
                if vals:
                    df = df[df[col_filtro].isin(vals)]

        with st.expander("➕ Colunas calculadas"):
            nome_nova = st.text_input("Nome da nova coluna", placeholder="comissao", key="etl_nova_col")
            expr = st.text_input("Expressão (Python)", placeholder="vendas * 0.1",
                                 help="Use nomes de colunas existentes como variáveis", key="etl_expr")
            if nome_nova and expr and st.button("Aplicar", key="etl_aplicar_col"):
                try:
                    df[nome_nova] = df.eval(expr)
                    st.success(f"Coluna '{nome_nova}' criada!")
                except Exception as e:
                    st.error(f"Erro: {e}")

        with st.expander("🗑️ Remover colunas"):
            remover = st.multiselect("Selecione colunas para remover", df.columns, key="etl_remover")
            if remover:
                df = df.drop(columns=remover)

        with st.expander("📊 Agrupar e agregar"):
            col_grupo = st.multiselect("Agrupar por", df.columns, key="etl_grupo")
            col_agreg = st.selectbox("Coluna para agregar", df.columns, key="etl_agreg")
            func_agreg = st.selectbox("Função", ["sum", "mean", "count", "max", "min"], key="etl_func")
            if col_grupo and col_agreg and st.button("Agrupar", key="etl_agrupar"):
                df = df.groupby(col_grupo)[col_agreg].agg(func_agreg).reset_index()

        with st.expander("📅 Extrair data"):
            cols_date = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
            if cols_date:
                col_data = st.selectbox("Coluna de data", cols_date, key="etl_data")
                ext = st.multiselect("Extrair", ["ano", "mês", "dia", "trimestre", "dia_da_semana", "semana"],
                                     default=["ano", "mês"], key="etl_ext")
                if ext and st.button("Extrair", key="etl_extrair"):
                    for e in ext:
                        if e == "ano": df[f"{col_data}_ano"] = df[col_data].dt.year
                        elif e == "mês": df[f"{col_data}_mes"] = df[col_data].dt.month
                        elif e == "dia": df[f"{col_data}_dia"] = df[col_data].dt.day
                        elif e == "trimestre": df[f"{col_data}_trimestre"] = df[col_data].dt.quarter
                        elif e == "dia_da_semana": df[f"{col_data}_dow"] = df[col_data].dt.dayofweek
                        elif e == "semana": df[f"{col_data}_semana"] = df[col_data].dt.isocalendar().week.astype(int)

        with st.expander("🔗 Ordenar"):
            col_ord = st.selectbox("Ordenar por", df.columns, key="etl_ord")
            asc = st.checkbox("Ascendente", True, key="etl_asc")
            if col_ord:
                df = df.sort_values(col_ord, ascending=asc)

        # Preview
        st.markdown("---")
        st.markdown(f"**Resultado:** {len(df)} linhas × {len(df.columns)} colunas")
        st.dataframe(df.head(50), use_container_width=True)

        col_apl, col_res = st.columns(2)
        with col_apl:
            if st.button("✅ Aplicar Transformações", type="primary", use_container_width=True):
                antes = st.session_state.etl_df.shape
                st.session_state.etl_df = df.copy()
                st.session_state.etl_history.append((f"Transformação #{len(st.session_state.etl_history)}", df.shape))
                st.success(f"{antes[0]}→{df.shape[0]} linhas, {antes[1]}→{df.shape[1]} colunas")
                st.rerun()
        with col_res:
            if st.button("↩️ Resetar", use_container_width=True):
                st.session_state.etl_df = None
                st.session_state.etl_history = []
                st.rerun()

    with tab_saida:
        if st.session_state.etl_df is None:
            st.info("Processe os dados primeiro na aba 'Transformações'")
            return

        df_final = st.session_state.etl_df
        st.success(f"✅ Pronto para exportar: {len(df_final)} registros × {len(df_final.columns)} colunas")

        # Histórico
        if st.session_state.etl_history:
            st.markdown("**Histórico de transformações:**")
            for passo, (antes, depois) in enumerate(st.session_state.etl_history):
                st.caption(f"  {passo+1}. {antes} → {depois}")

        st.markdown("**Destino da saída:**")
        destino = st.radio("", ["Dataset CLEVER", "Download", "Google Sheets", "Nova fonte de dados"])

        if destino == "Dataset CLEVER":
            nome_ds = st.text_input("Nome do dataset", placeholder="Ex: Vendas Transformadas")
            if st.button("💾 Salvar como Dataset", type="primary"):
                from modules.database import get_tenant_id, current_user, insert_record
                import json
                tenant_id = get_tenant_id()
                user = current_user()
                # Salva dados serializados como JSON no campo config
                dados_json = df_final.to_json(orient="records", force_ascii=False)
                result = insert_record("datasets", {
                    "tenant_id": tenant_id,
                    "nome": nome_ds,
                    "sql_query": "",  # dados inline
                    "config": json.dumps({"dados": dados_json}),
                    "criado_por": user.get("id")
                })
                if "error" not in result:
                    st.success(f"Dataset '{nome_ds}' salvo!")
                    st.rerun()

        elif destino == "Download":
            fmt = st.selectbox("Formato", ["CSV", "JSON", "Excel"])
            if fmt == "CSV":
                csv = df_final.to_csv(index=False).encode("utf-8-sig")
                st.download_button("📥 Baixar CSV", csv, "etl_output.csv", "text/csv")
            elif fmt == "JSON":
                js = df_final.to_json(orient="records", force_ascii=False).encode("utf-8")
                st.download_button("📥 Baixar JSON", js, "etl_output.json", "application/json")
            elif fmt == "Excel":
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as w:
                    df_final.to_excel(w, index=False, sheet_name="ETL")
                st.download_button("📥 Baixar Excel", buffer.getvalue(), "etl_output.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        elif destino == "Google Sheets":
            try:
                import gspread
                from oauth2client.service_account import ServiceAccountCredentials
                sa_json = st.secrets.get("gcp_service_account_json")
                if not sa_json:
                    st.warning("Google Sheets não configurado")
                else:
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(sa_json), scope)
                    client = gspread.authorize(creds)
                    titulo_sheet = f"CLEVER-ETL {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    sh = client.create(titulo_sheet)
                    ws = sh.get_worksheet(0)
                    ws.update_title("ETL")
                    ws.update([df_final.columns.values.tolist()] + df_final.values.tolist())
                    st.success(f"✅ Exportado: [Abrir]({sh.url})")
            except Exception as e:
                st.error(f"Erro: {e}")

        elif destino == "Nova fonte de dados":
            st.info("Use a aba 'Nova Fonte' na página de Fontes de Dados para salvar permanentemente.")
