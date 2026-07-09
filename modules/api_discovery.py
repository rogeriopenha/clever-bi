import streamlit as st
import json
import requests
import re
import pandas as pd
from urllib.parse import urlparse, urljoin
from datetime import datetime

def descobrir_api(base_url: str, headers: dict = None) -> dict:
    resultado = {
        "nome": "",
        "versao": "",
        "endpoints": [],
        "erro": None
    }

    if not headers:
        headers = {"Accept": "application/json"}

    # 1. Tenta padrões comuns de OpenAPI/Swagger
    spec = _tentar_swagger(base_url, headers)
    if spec:
        resultado.update(_parsear_swagger(spec))
        return resultado

    # 2. Tenta GraphQL introspection
    graphql = _tentar_graphql(base_url, headers)
    if graphql:
        resultado.update(graphql)
        return resultado

    # 3. Tenta descobrir endpoints comuns
    endpoints_comuns = _tentar_endpoints_comuns(base_url, headers)
    if endpoints_comuns:
        resultado["endpoints"] = endpoints_comuns
        resultado["nome"] = "API (descoberta parcial)"
        return resultado

    resultado["erro"] = "Não foi possível descobrir endpoints automaticamente. Tente especificar manualmente."
    return resultado

def _tentar_swagger(base_url: str, headers: dict) -> dict:
    # Remove trailing slash
    base = base_url.rstrip("/")

    # Padrões de URLs de spec
    padroes = [
        "/swagger.json",
        "/swagger/v1/swagger.json",
        "/api/swagger.json",
        "/api/docs/swagger.json",
        "/openapi.json",
        "/api/openapi.json",
        "/docs/openapi.json",
        "/v1/swagger.json",
        "/v2/swagger.json",
        "/v3/swagger.json",
        "/api/v1/swagger.json",
        "/api/v2/swagger.json",
        "/api/v3/swagger.json",
        "/doc/swagger.json",
        "/documentation/swagger.json",
        "/spec",
        "/api/spec",
        "/swagger",
        "/api/swagger",
        "/docs",
        "/api/docs",
    ]

    for padrao in padroes:
        url = urljoin(base, padrao)
        try:
            resp = requests.get(url, headers=headers, timeout=10, verify=False)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if "openapi" in data or "swagger" in data:
                        return data
                    if "paths" in data and isinstance(data["paths"], dict):
                        return data
                except:
                    pass
        except:
            continue
    return None

def _parsear_swagger(spec: dict) -> dict:
    info = spec.get("info", {})
    nome = info.get("title", "API sem nome")
    versao = info.get("version", "desconhecida")

    endpoints = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ("get", "post", "put", "delete", "patch"):
                continue

            endpoint = {
                "path": path,
                "method": method.upper(),
                "summary": details.get("summary", ""),
                "description": details.get("description", ""),
                "operation_id": details.get("operationId", ""),
                "tags": details.get("tags", []),
                "parameters": [],
                "responses": []
            }

            # Parâmetros
            for param in details.get("parameters", []):
                endpoint["parameters"].append({
                    "nome": param.get("name", ""),
                    "in": param.get("in", ""),
                    "type": param.get("schema", {}).get("type", "string") if "schema" in param else "string",
                    "required": param.get("required", False),
                    "description": param.get("description", "")
                })

            # Responses
            for status, resp_data in details.get("responses", {}).items():
                endpoint["responses"].append({
                    "status": status,
                    "description": resp_data.get("description", "")
                })

            endpoints.append(endpoint)

    # Agrupa por tag
    endpoints_agrupados = {}
    for ep in endpoints:
        tag = ep["tags"][0] if ep["tags"] else "Geral"
        if tag not in endpoints_agrupados:
            endpoints_agrupados[tag] = []
        endpoints_agrupados[tag].append(ep)

    return {
        "nome": nome,
        "versao": versao,
        "endpoints": endpoints,
        "endpoints_agrupados": endpoints_agrupados,
        "erro": None
    }

def _tentar_graphql(base_url: str, headers: dict) -> dict:
    query = {"query": "{ __schema { types { name fields { name } } } }"}
    try:
        resp = requests.post(base_url, json=query, headers=headers, timeout=10, verify=False)
        if resp.status_code == 200 and "data" in resp.json():
            data = resp.json()["data"]
            tipos = data.get("__schema", {}).get("types", [])
            endpoints = []
            for t in tipos:
                if t.get("name", "").startswith("Query"):
                    for f in t.get("fields", []):
                        endpoints.append({
                            "path": f["name"],
                            "method": "QUERY",
                            "summary": f"GraphQL query: {f['name']}",
                            "tags": ["GraphQL"]
                        })
            return {"nome": "GraphQL API", "versao": "GraphQL", "endpoints": endpoints}
    except:
        pass
    return None

def _tentar_endpoints_comuns(base_url: str, headers: dict) -> list:
    base = base_url.rstrip("/")
    endpoints = []
    candidatos = [
        "/api/orders", "/orders", "/pedidos", "/vendas",
        "/api/products", "/products", "/produtos",
        "/api/customers", "/customers", "/clientes",
        "/api/users", "/users", "/usuarios",
        "/health", "/status", "/api/status",
        "/api/v1", "/v1",
    ]

    for path in candidatos:
        url = urljoin(base, path)
        try:
            resp = requests.get(url, headers=headers, timeout=5, verify=False)
            if resp.status_code in (200, 201):
                try:
                    sample = resp.json()
                    endpoints.append({
                        "path": path,
                        "method": "GET",
                        "summary": f"Possível endpoint. Status: {resp.status_code}. Amostra: {json.dumps(sample)[:100]}...",
                        "tags": ["Descoberta automática"],
                        "parameters": [],
                        "responses": [{"status": str(resp.status_code), "description": "OK"}]
                    })
                except:
                    endpoints.append({
                        "path": path,
                        "method": "GET",
                        "summary": f"Respondeu com status {resp.status_code}",
                        "tags": ["Descoberta automática"],
                        "parameters": [],
                        "responses": [{"status": str(resp.status_code), "description": "OK"}]
                    })
        except:
            continue

    return endpoints

def testar_endpoint(base_url: str, path: str, method: str, headers: dict = None,
                    params: dict = None, body: dict = None) -> dict:
    url = urljoin(base_url.rstrip("/"), path)
    if not headers:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=15, verify=False)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=body, timeout=15, verify=False)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=body, timeout=15, verify=False)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=15, verify=False)
        else:
            return {"erro": f"Método {method} não suportado"}

        resultado = {
            "status": resp.status_code,
            "ok": resp.ok,
            "tempo_ms": resp.elapsed.total_seconds() * 1000,
            "headers": dict(resp.headers),
        }

        try:
            resultado["dados"] = resp.json()
        except:
            resultado["dados"] = resp.text[:500]

        return resultado
    except requests.exceptions.Timeout:
        return {"erro": "Timeout após 15 segundos", "status": 0, "ok": False}
    except requests.exceptions.ConnectionError:
        return {"erro": "Erro de conexão — verifique a URL e o firewall", "status": 0, "ok": False}
    except Exception as e:
        return {"erro": str(e), "status": 0, "ok": False}

def gerar_query_sql(endpoint: dict, amostra: dict = None) -> str:
    path = endpoint["path"]
    op = endpoint.get("operation_id", "")

    if amostra and isinstance(amostra, list) and len(amostra) > 0:
        item = amostra[0]
    elif amostra and isinstance(amostra, dict):
        item = amostra
    else:
        item = {}

    if not item:
        return f"-- Endpoint: {endpoint['method']} {path}\n-- Conecte o endpoint como fonte de dados primeiro."

    colunas = list(item.keys())[:20]
    nome_tabela = op or path.strip("/").replace("/", "_").replace("-", "_")

    sql = f"-- Dados de: {endpoint['summary'] or path}\n"
    sql += f"-- Endpoint: {endpoint['method']} {path}\n\n"
    sql += f"SELECT\n"
    for c in colunas:
        sql += f"    data->>'{c}' AS {c},\n"
    sql = sql.rstrip(",\n")
    sql += f"\nFROM api_endpoint('{path}', '{endpoint['method']}')\n"
    sql += f"LIMIT 100;\n"

    return sql

def wizard_descoberta_api():
    st.markdown("### 🔍 Descobridor de API")
    st.markdown("""
        <p style="color:#6b7fa3;font-size:0.9rem">
            Cole a URL base da API e o CLEVER vai tentar descobrir automaticamente 
            os endpoints disponíveis, documentação e propor a integração.
        </p>
    """, unsafe_allow_html=True)

    if "api_descoberta" not in st.session_state:
        st.session_state.api_descoberta = {}

    with st.form("api_discovery_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            base_url = st.text_input("URL Base da API",
                placeholder="https://api.copastur.com.br",
                value=st.session_state.get("api_url_input", ""))
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            tipo_auth = st.selectbox("Tipo de Autenticação",
                ["Nenhuma", "Bearer Token", "Basic Auth", "API Key"])

        headers = {}
        if tipo_auth == "Bearer Token":
            token = st.text_input("Bearer Token", type="password",
                placeholder="eyJhbGciOi...")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        elif tipo_auth == "Basic Auth":
            c1, c2 = st.columns(2)
            with c1:
                user = st.text_input("Usuário")
            with c2:
                password = st.text_input("Senha", type="password")
            if user and password:
                import base64
                encoded = base64.b64encode(f"{user}:{password}".encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"
        elif tipo_auth == "API Key":
            c1, c2 = st.columns(2)
            with c1:
                key_name = st.text_input("Nome do header", value="X-API-Key")
            with c2:
                key_value = st.text_input("Valor da API Key", type="password")
            if key_name and key_value:
                headers[key_name] = key_value

        discovered = st.form_submit_button("🔍 Descobrir API", type="primary", use_container_width=True)

    if discovered and base_url:
        with st.spinner("Vasculhando endpoints..."):
            resultado = descobrir_api(base_url, headers)
            st.session_state.api_descoberta = {
                "base_url": base_url,
                "headers": headers,
                "resultado": resultado
            }
            st.rerun()

    resultado = st.session_state.api_descoberta.get("resultado")

    if resultado and resultado.get("erro"):
        st.warning(resultado["erro"])
        st.session_state.api_descoberta = {}
        return None

    if resultado:
        endpoints = resultado.get("endpoints", [])
        nome_api = resultado.get("nome", "API")
        versao = resultado.get("versao", "")

        st.success(f"✅ **{nome_api}** {f'v{versao}' if versao else ''} — {len(endpoints)} endpoints encontrados")

        endpoints_agrupados = resultado.get("endpoints_agrupados", {})
        if not endpoints_agrupados:
            endpoints_agrupados = {"Todos": endpoints}

        # Abas por tag
        tags = list(endpoints_agrupados.keys())
        if tags:
            tab_titles = [f"{t}" for t in tags]
            tabs = st.tabs(tab_titles)
            for ti, tag in enumerate(tags):
                with tabs[ti]:
                    eps = endpoints_agrupados[tag]
                    for ep in eps:
                        with st.expander(f"{ep['method']} {ep['path']}"):
                            if ep["summary"]:
                                st.markdown(f"**{ep['summary']}**")
                            if ep["description"]:
                                st.markdown(f"_{ep['description']}_")

                            if ep["parameters"]:
                                st.markdown("**Parâmetros:**")
                                df_params = pd.DataFrame(ep["parameters"])
                                st.dataframe(df_params, use_container_width=True, height=min(200, len(df_params)*35))

                            # Botão de teste
                            col_a, col_b = st.columns([1, 3])
                            with col_a:
                                if st.button(f"🧪 Testar", key=f"test_{ep['path']}_{ep['method']}"):
                                    teste = testar_endpoint(base_url, ep["path"], ep["method"], headers)
                                    if "erro" in teste:
                                        st.error(teste["erro"])
                                    else:
                                        st.code(f"Status: {teste['status']} | Tempo: {teste['tempo_ms']:.0f}ms")
                                        st.json(teste.get("dados", {})[:3] if isinstance(teste.get("dados"), list) else teste.get("dados", {}))
                            with col_b:
                                if st.button(f"📥 Importar como Dataset", key=f"import_{ep['path']}_{ep['method']}"):
                                    st.session_state.api_import = {
                                        "base_url": base_url,
                                        "headers": headers,
                                        "endpoint": ep
                                    }
                                    st.rerun()

        st.markdown("---")
        st.markdown(f"**Endpoints encontrados:** {len(endpoints)} | **Documentação gerada** ✅")

        return resultado

    return None

def tela_importar_api():
    if "api_import" not in st.session_state:
        st.info("Nenhum endpoint selecionado para importação.")
        return

    imp = st.session_state.api_import
    ep = imp["endpoint"]

    st.markdown(f"### 📥 Importar: {ep['method']} {ep['path']}")
    st.markdown(f"**{ep.get('summary', '')}**")

    with st.form("confirm_import"):
        nome_dataset = st.text_input("Nome do dataset",
            value=ep.get("operation_id", "") or ep["path"].strip("/").replace("/", "_").replace("-", "_"),
            placeholder="Ex: pedidos_aprovacao")

        params = {}
        for p in ep.get("parameters", []):
            if p.get("in") == "query":
                params[p["nome"]] = st.text_input(
                    f"{p['nome']} {'*' if p.get('required') else ''}",
                    value=p.get("default", ""),
                    placeholder=p.get("description", "")
                )

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salvar Dataset", type="primary", use_container_width=True):
                st.session_state.api_dataset_config = {
                    "nome": nome_dataset,
                    "base_url": imp["base_url"],
                    "headers": imp["headers"],
                    "endpoint_path": ep["path"],
                    "endpoint_method": ep["method"],
                    "params": params
                }
                st.success(f"Dataset '{nome_dataset}' salvo!")
                st.session_state.api_import = None
                st.rerun()
        with col2:
            if st.form_submit_button("Cancelar", use_container_width=True):
                st.session_state.api_import = None
                st.rerun()
