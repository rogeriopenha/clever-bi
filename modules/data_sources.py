import streamlit as st
import pandas as pd
import json
from modules.database import insert_record, query_native, get_tenant_id, current_user, load_csv

from modules.i18n import t

def gerenciar_fontes():
    st.subheader(t("fontes.titulo"))
    tenant_id = get_tenant_id()

    tab_nova, tab_lista, tab_api = st.tabs(["Nova Fonte", "Fontes Existentes", "🔍 API Discovery"])

    with tab_nova:
        with st.form("nova_fonte"):
            nome = st.text_input("Nome da fonte", placeholder="Ex: Vendas Copastur")
            tipo = st.selectbox("Tipo", ["api", "supabase", "google_sheets", "csv"])
            config = {}

            if tipo == "api":
                st.markdown("**🔌 Conexão API**")
                config["doc_url"] = st.text_input(
                    "URL da Documentação (Swagger/OpenAPI)",
                    placeholder="https://api.copastur.com.br/swagger.json",
                    help="URL do arquivo de especificação OpenAPI/Swagger para descoberta automática"
                )
                config["url"] = st.text_input(
                    "URL Base da API",
                    placeholder="https://api.copastur.com.br"
                )
                config["method"] = st.selectbox("Método Principal", ["GET", "POST"])
                config["auth_type"] = st.selectbox(
                    "Tipo de Autenticação",
                    ["Nenhuma", "Bearer Token", "Basic Auth", "API Key"]
                )
                if config["auth_type"] == "Bearer Token":
                    config["token"] = st.text_input("Bearer Token", type="password",
                        placeholder="eyJhbGciOi...")
                elif config["auth_type"] == "Basic Auth":
                    c1, c2 = st.columns(2)
                    with c1:
                        config["auth_user"] = st.text_input("Usuário")
                    with c2:
                        config["auth_pass"] = st.text_input("Senha", type="password")
                elif config["auth_type"] == "API Key":
                    c1, c2 = st.columns(2)
                    with c1:
                        config["key_name"] = st.text_input("Nome do Header", value="X-API-Key")
                    with c2:
                        config["key_value"] = st.text_input("Valor da API Key", type="password")
                config["headers"] = st.text_area(
                    "Headers Adicionais (JSON)",
                    value="{}",
                    help='Ex: {"Accept": "application/json"}'
                )

            elif tipo == "google_sheets":
                config["url"] = st.text_input("URL da planilha", placeholder="https://docs.google.com/spreadsheets/d/...")
                config["aba"] = st.text_input("Aba (opcional)", placeholder="Sheet1")

            elif tipo == "csv":
                arquivo = st.file_uploader("Upload do arquivo", type=["csv", "xlsx"])
                if arquivo:
                    config["nome_arquivo"] = arquivo.name
                    df = load_csv(arquivo)
                    if not df.empty:
                        st.dataframe(df.head(), use_container_width=True)
                        config["colunas"] = list(df.columns)
                        st.session_state["csv_temp_" + nome] = df.to_json()

            elif tipo == "supabase":
                st.markdown("**🗄️ Conexão Supabase**")
                config["tabela"] = st.text_input("Nome da tabela no Supabase",
                    placeholder="Ex: pedidos, clientes, produtos")

            if st.form_submit_button("Salvar Fonte", type="primary", use_container_width=True):
                result = insert_record("fontes_dados", {
                    "tenant_id": tenant_id,
                    "nome": nome,
                    "tipo": tipo,
                    "config": json.dumps(config),
                    "criado_por": current_user().get("id")
                })
                if "error" not in result:
                    st.success(f"Fonte '{nome}' criada!")
                    st.rerun()

    with tab_lista:
        fontes = query_native("fontes_dados", filters={"tenant_id": tenant_id})
        if not fontes.empty:
            for _, f in fontes.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{f['nome']}** `{f['tipo']}`")
                    config = f.get("config", {})
                    if isinstance(config, str):
                        config = json.loads(config)
                    if isinstance(config, dict) and "url" in config:
                        st.caption(config["url"])
                with col2:
                    if st.button("🗑️", key=f"del_fonte_{f['id']}"):
                        from modules.database import delete_record
                        delete_record("fontes_dados", "id", f["id"])
                        st.rerun()
        else:
            st.info("Nenhuma fonte cadastrada ainda.")

    with tab_api:
        from modules.api_discovery import wizard_descoberta_api
        wizard_descoberta_api()

def listar_datasets():
    tenant_id = get_tenant_id()
    datasets = query_native("datasets", filters={"tenant_id": tenant_id})
    if not datasets.empty:
        return datasets
    return pd.DataFrame()

def criar_dataset(nome: str, sql: str, fonte_id: str = None):
    tenant_id = get_tenant_id()
    return insert_record("datasets", {
        "tenant_id": tenant_id,
        "nome": nome,
        "sql_query": sql,
        "fonte_id": fonte_id,
        "criado_por": current_user().get("id")
    })

def executar_dataset(dataset_id: str) -> pd.DataFrame:
    datasets = listar_datasets()
    if datasets.empty:
        return pd.DataFrame()
    ds = datasets[datasets["id"] == dataset_id]
    if ds.empty:
        return pd.DataFrame()
    ds = ds.iloc[0]
    sql = ds.get("sql_query", "")
    if sql:
        from modules.database import query_supabase
        return query_supabase(sql)
    return pd.DataFrame()

def preview_fonte(tipo: str, config: dict) -> pd.DataFrame:
    if tipo == "csv":
        return pd.DataFrame()
    elif tipo == "supabase":
        from modules.database import query_native
        return query_native(config.get("tabela", ""))
    elif tipo == "google_sheets":
        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            sa_json = st.secrets.get("gcp_service_account_json")
            if sa_json:
                creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(sa_json), scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(config["url"])
                ws = sheet.worksheet(config.get("aba", sheet.worksheets()[0].title))
                rows = ws.get_all_values()
                if rows:
                    return pd.DataFrame(rows[1:], columns=rows[0])
        except Exception as e:
            st.warning(f"Erro ao carregar Google Sheets: {e}")
    return pd.DataFrame()
