import streamlit as st
import pandas as pd
import json
import requests
from urllib.parse import urljoin
import base64
from modules.database import insert_record, query_native, get_tenant_id, current_user, load_csv

from modules.i18n import t

def gerenciar_fontes():
    st.subheader(t("fontes.titulo"))
    tenant_id = get_tenant_id()

    tab_nova, tab_lista, tab_api = st.tabs(["Nova Fonte", "Fontes Existentes", "🔍 API Discovery"])

    with tab_nova:
        tipo = st.selectbox("Tipo", [
            "", "api", "copastur", "proceda", "mysql", "sql_server", "postgresql", "mongodb",
            "supabase", "google_sheets", "excel", "csv"
        ])

        if not tipo:
            st.info("👆 Selecione um tipo de fonte acima para configurar")

        # Auth fields outside form for reactivity
        if tipo == "api":
            st.markdown("**🔐 Autenticação**")
            st.selectbox("Tipo de Autenticação",
                ["Nenhuma", "Bearer Token", "Basic Auth", "API Key"],
                key="auth_type_outside")
            auth_type = st.session_state.get("auth_type_outside", "Nenhuma")
            if auth_type == "Bearer Token":
                st.text_input("Bearer Token", type="password",
                    placeholder="eyJhbGciOi...", key="api_bearer_token")
            elif auth_type == "Basic Auth":
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Usuário", key="api_basic_user")
                with c2:
                    st.text_input("Senha", type="password", key="api_basic_pass")
            elif auth_type == "API Key":
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Nome do Header", value="X-API-Key", key="api_key_name")
                with c2:
                    st.text_input("Valor da API Key", type="password", key="api_key_value")
            st.text_area("Headers Adicionais (JSON)", value="{}",
                help='Ex: {"Accept": "application/json"}', key="api_headers")

        with st.form("nova_fonte"):
            nome = st.text_input("Nome da fonte", placeholder="Ex: Vendas Copastur") if tipo else ""
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
                config["auth_type"] = st.session_state.get("auth_type_outside", "Nenhuma")
                if config["auth_type"] == "Bearer Token":
                    config["token"] = st.session_state.get("api_bearer_token", "")
                elif config["auth_type"] == "Basic Auth":
                    config["auth_user"] = st.session_state.get("api_basic_user", "")
                    config["auth_pass"] = st.session_state.get("api_basic_pass", "")
                elif config["auth_type"] == "API Key":
                    config["key_name"] = st.session_state.get("api_key_name", "X-API-Key")
                    config["key_value"] = st.session_state.get("api_key_value", "")
                config["headers"] = st.session_state.get("api_headers", "{}")
                config["endpoint_preview"] = st.text_input(
                    "Endpoint de teste (opcional)",
                    value=config.get("endpoint_preview", "/v2/api/Order/List"),
                    placeholder="/v2/api/Order/List",
                    help="Caminho do endpoint para testar a conexão"
                )

            elif tipo == "copastur":
                st.markdown("**🏢 Copastur — API Sankhya**")
                st.caption("Integração com o sistema Sankhya da Copastur")
                config["tipo_conexao"] = st.selectbox(
                    "Tipo de Conexão",
                    ["API Sankhya", "Google Sheets (fallback)"]
                )

                if config["tipo_conexao"] == "API Sankhya":
                    config["sankhya_url"] = st.text_input(
                        "URL do Servidor Sankhya",
                        placeholder="https://api.sankhya.com.br/service",
                        value=config.get("sankhya_url", "https://api.sankhya.com.br/service")
                    )
                    config["sankhya_token"] = st.text_input(
                        "Token de Integração",
                        type="password",
                        placeholder="Cole o token gerado no Sankhya",
                        help="Token gerado no módulo de integrações do Sankhya"
                    )
                    config["sankhya_usuario"] = st.text_input("Usuário Sankhya", placeholder="api_user")
                    config["sankhya_senha"] = st.text_input("Senha", type="password")
                    config["entidade"] = st.selectbox(
                        "Entidade / Dataset",
                        ["Vendas", "Pedidos", "Clientes", "Produtos", "Financeiro",
                         "Compras", "Estoque", "Faturamento", "CRM", "Custom (SQL)"]
                    )
                    if config["entidade"] == "Custom (SQL)":
                        config["query_sankhya"] = st.text_area(
                            "Query SQL (MSSQL)",
                            placeholder="SELECT * FROM VENDAS WHERE DATA >= '2024-01-01'",
                            help="Query no dialect MSSQL do Sankhya"
                        )
                    config["periodo_automatico"] = st.checkbox("Buscar período automático (últimos 30 dias)",
                        value=config.get("periodo_automatico", True))
                    c1, c2 = st.columns(2)
                    with c1:
                        config["data_inicio"] = st.date_input("Data início (opcional)")
                    with c2:
                        config["data_fim"] = st.date_input("Data fim (opcional)")

                else:
                    config["sheets_url"] = st.text_input(
                        "URL da Planilha Google Sheets",
                        placeholder="https://docs.google.com/spreadsheets/d/..."
                    )
                    config["sheets_aba"] = st.text_input("Aba", value="Sheet1")
                    config["sheets_intervalo"] = st.text_input(
                        "Intervalo (opcional)",
                        placeholder="A:Z",
                        help="Ex: A:Z ou A1:Z1000"
                    )

            elif tipo == "proceda":
                st.markdown("**📂 Proceda — Arquivos do Sistema**")
                st.caption("Importação de arquivos do sistema Proceda")
                config["tipo_arquivo"] = st.selectbox(
                    "Tipo de Arquivo",
                    ["Ocorrências (ocoren)", "Conhecimentos (conemb)", "Documentos Cobrança (doccob)"]
                )

                if config["tipo_arquivo"] == "Ocorrências (ocoren)":
                    config["sub_tipo"] = "ocoren"
                    st.markdown("**Ocorrências — Registro de eventos e ocorrências do sistema**")
                    config["formato"] = st.selectbox(
                        "Formato do arquivo",
                        ["TXT (delimitado)", "CSV", "JSON"]
                    )
                    arquivo = st.file_uploader(
                        "Upload do arquivo de ocorrências",
                        type=["txt", "csv", "json"],
                        key="ocoren"
                    )
                    if arquivo:
                        config["nome_arquivo"] = arquivo.name
                        try:
                            df = load_csv(arquivo)
                            if not df.empty:
                                st.dataframe(df.head(), use_container_width=True)
                                config["colunas"] = list(df.columns)
                                st.session_state["proceda_ocoren_" + nome] = df.to_json()
                        except:
                            st.info("Prévia não disponível para este formato")

                elif config["tipo_arquivo"] == "Conhecimentos (conemb)":
                    config["sub_tipo"] = "conemb"
                    st.markdown("**Conhecimentos de Embarque — Documentos de transporte e logística**")
                    config["formato"] = st.selectbox(
                        "Formato do arquivo",
                        ["TXT (delimitado)", "CSV", "XML", "JSON"],
                        key="fmt_conemb"
                    )
                    arquivo = st.file_uploader(
                        "Upload do arquivo de conhecimentos",
                        type=["txt", "csv", "xml", "json"],
                        key="conemb"
                    )
                    if arquivo:
                        config["nome_arquivo"] = arquivo.name
                        try:
                            df = load_csv(arquivo)
                            if not df.empty:
                                st.dataframe(df.head(), use_container_width=True)
                                config["colunas"] = list(df.columns)
                                st.session_state["proceda_conemb_" + nome] = df.to_json()
                        except:
                            st.info("Prévia não disponível para este formato")

                elif config["tipo_arquivo"] == "Documentos Cobrança (doccob)":
                    config["sub_tipo"] = "doccob"
                    st.markdown("**Documentos de Cobrança — Boletos, faturas e títulos**")
                    config["formato"] = st.selectbox(
                        "Formato do arquivo",
                        ["CSV", "TXT (delimitado)", "JSON", "XML"],
                        key="fmt_doccob"
                    )
                    arquivo = st.file_uploader(
                        "Upload do arquivo de cobrança",
                        type=["csv", "txt", "json", "xml"],
                        key="doccob"
                    )
                    if arquivo:
                        config["nome_arquivo"] = arquivo.name
                        try:
                            df = load_csv(arquivo)
                            if not df.empty:
                                st.dataframe(df.head(), use_container_width=True)
                                config["colunas"] = list(df.columns)
                                st.session_state["proceda_doccob_" + nome] = df.to_json()
                        except:
                            st.info("Prévia não disponível para este formato")
                config["periodo_padrao"] = st.text_input(
                    "Período padrão (opcional)",
                    placeholder="Ex: Mês atual, Últimos 30 dias"
                )

            elif tipo == "mysql":
                st.markdown("**🐬 MySQL**")
                config["host"] = st.text_input("Host", value="localhost", placeholder="localhost")
                config["port"] = st.number_input("Porta", value=3306, min_value=1, max_value=65535)
                config["database"] = st.text_input("Banco de Dados", placeholder="meu_banco")
                config["user"] = st.text_input("Usuário", placeholder="root")
                config["password"] = st.text_input("Senha", type="password")
                config["query"] = st.text_area("Query SQL", placeholder="SELECT * FROM vendas LIMIT 100",
                    help="Query para extrair os dados")

            elif tipo == "sql_server":
                st.markdown("**🗄️ SQL Server**")
                config["host"] = st.text_input("Host", value="localhost", placeholder="localhost")
                config["port"] = st.number_input("Porta", value=1433, min_value=1, max_value=65535)
                config["database"] = st.text_input("Banco de Dados", placeholder="meu_banco")
                config["user"] = st.text_input("Usuário", placeholder="sa")
                config["password"] = st.text_input("Senha", type="password")
                config["query"] = st.text_area("Query SQL", placeholder="SELECT * FROM vendas LIMIT 100",
                    help="Query para extrair os dados")

            elif tipo == "postgresql":
                st.markdown("**🐘 PostgreSQL**")
                config["host"] = st.text_input("Host", value="localhost", placeholder="localhost")
                config["port"] = st.number_input("Porta", value=5432, min_value=1, max_value=65535)
                config["database"] = st.text_input("Banco de Dados", placeholder="meu_banco")
                config["user"] = st.text_input("Usuário", placeholder="postgres")
                config["password"] = st.text_input("Senha", type="password")
                config["query"] = st.text_area("Query SQL", placeholder="SELECT * FROM vendas LIMIT 100",
                    help="Query para extrair os dados")

            elif tipo == "mongodb":
                st.markdown("**🍃 MongoDB**")
                config["uri"] = st.text_input("Connection String (URI)",
                    placeholder="mongodb://usuario:senha@localhost:27017/meu_banco")
                config["database"] = st.text_input("Banco de Dados", placeholder="meu_banco")
                config["collection"] = st.text_input("Coleção", placeholder="vendas")
                config["query"] = st.text_area("Filtro (JSON)", value="{}",
                    help='Ex: {"status": "ativo"}')

            elif tipo == "google_sheets":
                st.markdown("**📊 Google Sheets**")
                config["url"] = st.text_input("URL da planilha", placeholder="https://docs.google.com/spreadsheets/d/...")
                config["aba"] = st.text_input("Aba (opcional)", placeholder="Sheet1")

            elif tipo == "excel":
                st.markdown("**📗 Excel**")
                arquivo = st.file_uploader("Upload do arquivo Excel", type=["xlsx", "xls"])
                if arquivo:
                    config["nome_arquivo"] = arquivo.name
                    df = load_csv(arquivo)
                    if not df.empty:
                        st.dataframe(df.head(), use_container_width=True)
                        config["colunas"] = list(df.columns)
                        config["planilha"] = st.text_input("Planilha/Aba", placeholder="Sheet1",
                            help="Nome da planilha dentro do arquivo (opcional)")
                        st.session_state["excel_temp_" + nome] = df.to_json()

            elif tipo == "csv":
                st.markdown("**📄 CSV**")
                arquivo = st.file_uploader("Upload do arquivo", type=["csv", "tsv"])
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

            if st.form_submit_button("Salvar Fonte", type="primary", use_container_width=True, disabled=not tipo):
                if not nome:
                    st.warning("Preencha o nome da fonte")
                else:
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
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{f['nome']}** `{f['tipo']}`")
                    config = f.get("config", {})
                    if isinstance(config, str):
                        config = json.loads(config)
                    if isinstance(config, dict) and "url" in config:
                        st.caption(config["url"])
                with col2:
                    if f["tipo"] == "api":
                        if st.button("🧪", key=f"test_fonte_{f['id']}", help="Testar conexão"):
                            with st.spinner("Testando..."):
                                preview = preview_fonte(f["tipo"], config)
                                if not preview.empty:
                                    st.success(f"{len(preview)} registros")
                                    st.dataframe(preview.head(10), use_container_width=True, height=200)
                                else:
                                    st.warning("Nenhum dado retornado")
                with col3:
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

def fetch_api_endpoint(
    base_url: str,
    endpoint_path: str,
    method: str = "GET",
    auth_type: str = "Nenhuma",
    auth_user: str = "",
    auth_pass: str = "",
    token: str = "",
    key_name: str = "",
    key_value: str = "",
    headers_json: str = "{}",
    params: dict = None
) -> pd.DataFrame:
    url = urljoin(base_url.rstrip("/"), endpoint_path)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    try:
        extra = json.loads(headers_json) if isinstance(headers_json, str) else headers_json
        headers.update(extra)
    except:
        pass

    if auth_type == "Bearer Token" and token:
        headers["Authorization"] = f"Bearer {token}"
    elif auth_type == "Basic Auth" and auth_user:
        encoded = base64.b64encode(f"{auth_user}:{auth_pass}".encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"
    elif auth_type == "API Key" and key_name and key_value:
        headers[key_name] = key_value

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=params, timeout=30, verify=False)
        else:
            return pd.DataFrame()

        if resp.status_code not in (200, 201):
            return pd.DataFrame()

        data = resp.json()

        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], list):
                return pd.DataFrame(data["data"])
            return pd.DataFrame([data])
        elif isinstance(data, list):
            return pd.DataFrame(data)

        return pd.DataFrame()
    except:
        return pd.DataFrame()


def preview_fonte(tipo: str, config: dict) -> pd.DataFrame:
    if tipo == "csv":
        return pd.DataFrame()
    elif tipo == "supabase":
        from modules.database import query_native
        return query_native(config.get("tabela", ""))
    elif tipo == "api":
        return fetch_api_endpoint(
            base_url=config.get("url", ""),
            endpoint_path=config.get("endpoint_preview", "/v2/api/Order/List"),
            method=config.get("method", "GET"),
            auth_type=config.get("auth_type", "Nenhuma"),
            auth_user=config.get("auth_user", ""),
            auth_pass=config.get("auth_pass", ""),
            token=config.get("token", ""),
            key_name=config.get("key_name", ""),
            key_value=config.get("key_value", ""),
            headers_json=config.get("headers", "{}"),
        )
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
