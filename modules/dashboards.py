import streamlit as st
import pandas as pd
import json
from datetime import datetime
from modules.database import insert_record, update_record, delete_record, query_native, get_tenant_id, current_user, load_csv
from modules.widgets import render_widget, editor_widget
from modules.data_sources import preview_fonte, listar_datasets, criar_dataset
from modules.i18n import t

def listar_dashboards():
    tenant_id = get_tenant_id()
    return query_native("dashboards", filters={"tenant_id": tenant_id})

def criar_dashboard(nome: str, descricao: str = ""):
    tenant_id = get_tenant_id()
    return insert_record("dashboards", {
        "tenant_id": tenant_id,
        "nome": nome,
        "descricao": descricao,
        "layout": json.dumps([]),
        "criado_por": current_user().get("id")
    })

def salvar_widget(dashboard_id: str, widget_data: dict):
    tenant_id = get_tenant_id()
    posicao = widget_data.get("posicao", {"x": 0, "y": 0, "w": 2, "h": 1})
    max_y = _proximo_y(dashboard_id)
    if posicao.get("y", 0) == 0:
        posicao["y"] = max_y
    return insert_record("widgets", {
        "dashboard_id": dashboard_id,
        "tenant_id": tenant_id,
        "tipo": widget_data["tipo"],
        "titulo": widget_data["titulo"],
        "config": json.dumps(widget_data["config"]),
        "posicao": json.dumps(posicao),
        "criado_por": current_user().get("id")
    })

def _proximo_y(dashboard_id: str) -> int:
    widgets = listar_widgets(dashboard_id)
    if widgets.empty:
        return 0
    max_y = 0
    for _, w in widgets.iterrows():
        p = parse_posicao(w)
        max_y = max(max_y, p["y"])
    return max_y + 1

def listar_widgets(dashboard_id: str):
    return query_native("widgets", filters={"dashboard_id": dashboard_id})

def parse_posicao(widget) -> dict:
    pos = widget.get("posicao", {})
    if isinstance(pos, str):
        try:
            pos = json.loads(pos)
        except:
            pos = {}
    return {
        "x": int(pos.get("x", 0)),
        "y": int(pos.get("y", 0)),
        "w": int(pos.get("w", 2)),
        "h": int(pos.get("h", 1))
    }

def render_dashboard(dashboard_id: str):
    dashboards = listar_dashboards()
    if dashboards.empty:
        st.info("Dashboard não encontrado")
        return

    dash = dashboards[dashboards["id"] == dashboard_id]
    if dash.empty:
        st.info("Dashboard não encontrado")
        return
    dash = dash.iloc[0]

    st.markdown(f"""
        <h1 style="color:#e8edf5;margin-bottom:0.25rem">{dash['nome']}</h1>
        <p style="color:#6b7fa3;margin-bottom:1.5rem">{dash.get('descricao', '')}</p>
    """, unsafe_allow_html=True)

    # Filtro de período
    with st.expander("📅 Filtro de Período", expanded=False):
        col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
        with col_p1:
            data_ini = st.date_input("Data início", value=None, key=f"di_{dashboard_id}")
        with col_p2:
            data_fim = st.date_input("Data fim", value=None, key=f"df_{dashboard_id}")
        with col_p3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Aplicar", key=f"filtro_{dashboard_id}"):
                st.session_state[f"periodo_{dashboard_id}"] = {
                    "inicio": str(data_ini) if data_ini else None,
                    "fim": str(data_fim) if data_fim else None
                }
                st.rerun()

    # Exportação
    with st.expander("📤 Exportar Dados", expanded=False):
        widgets = listar_widgets(dashboard_id)
        if not widgets.empty:
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                if st.button("📥 CSV", key=f"exp_csv_{dashboard_id}", use_container_width=True):
                    _exportar_dashboard(widgets, "csv")
            with col_e2:
                if st.button("📥 JSON", key=f"exp_json_{dashboard_id}", use_container_width=True):
                    _exportar_dashboard(widgets, "json")
            with col_e3:
                if st.button("📥 Excel", key=f"exp_xlsx_{dashboard_id}", use_container_width=True):
                    _exportar_dashboard(widgets, "excel")
            st.markdown("---")
            if st.button("📤 Exportar para Google Sheets", key=f"exp_gs_{dashboard_id}",
                         use_container_width=True, type="secondary"):
                _exportar_google_sheets(widgets, dash)
        else:
            st.info("Adicione widgets ao dashboard para exportar.")

    widgets = listar_widgets(dashboard_id)

    if widgets.empty:
        st.info("Este dashboard está vazio. Adicione widgets no modo edição.")
        return

    # Grid responsivo baseado na posicao
    grid_data = []
    for _, w in widgets.iterrows():
        p = parse_posicao(w)
        grid_data.append((p["y"], p["x"], p["w"], p["h"], w))

    grid_data.sort(key=lambda g: (g[0], g[1]))

    # Agrupa por linha (y)
    linhas = {}
    for y, x, w, h, widget in grid_data:
        if y not in linhas:
            linhas[y] = []
        linhas[y].append((x, w, h, widget))

    for y in sorted(linhas.keys()):
        items = sorted(linhas[y], key=lambda i: i[0])
        # Cada unidade de largura = 1 coluna em 4-column grid
        # Mapeia w={1..4} para proporcoes
        proporcoes = {1: 1, 2: 2, 3: 3, 4: 4}
        col_specs = []
        for x, w, h, widget in items:
            col_specs.append((proporcoes.get(w, 2), widget))

        if not col_specs:
            continue

        # Criar colunas com proporcoes
        total = sum(c[0] for c in col_specs)
        weights = [c[0] / total for c in col_specs]
        cols = st.columns(weights)

        for ci, (_, widget) in enumerate(col_specs):
            dados = _carregar_dados_widget(widget)
            with cols[ci]:
                with st.container():
                    render_widget(widget, dados)

def _carregar_dados_widget(widget) -> pd.DataFrame:
    config = widget.get("config", {})
    if isinstance(config, str):
        config = json.loads(config)

    dataset_id = widget.get("dataset_id")
    if dataset_id:
        from modules.data_sources import executar_dataset
        return executar_dataset(dataset_id)

    sql = widget.get("sql_query", "")
    if sql:
        from modules.database import query_supabase
        return query_supabase(sql)

    col_valor = config.get("coluna_valor", "")
    if col_valor or config:
        dados_demo = _dados_demo()
        if not dados_demo.empty:
            return dados_demo

    return pd.DataFrame()

def _dados_demo() -> pd.DataFrame:
    import numpy as np
    meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    return pd.DataFrame({
        "mes": meses,
        "vendas": np.random.randint(10000, 50000, 12),
        "meta": np.random.randint(15000, 45000, 12),
        "custo": np.random.randint(5000, 20000, 12),
        "produto": np.random.choice(["Arroz", "Feijão", "Óleo", "Açúcar", "Café"], 12),
        "regiao": np.random.choice(["Norte", "Sul", "Leste", "Oeste"], 12),
        "vendedor": np.random.choice(["João", "Maria", "Carlos"], 12)
    })

def editar_dashboard(dashboard_id: str):
    tenant_id = get_tenant_id()

    dashboards = listar_dashboards()
    dash = dashboards[dashboards["id"] == dashboard_id].iloc[0] if not dashboards.empty else None

    if dash is None:
        st.info("Dashboard não encontrado")
        return

    with st.form("edit_dashboard"):
        nome = st.text_input("Nome do dashboard", value=dash["nome"])
        descricao = st.text_area("Descrição", value=dash.get("descricao", ""))
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
                update_record("dashboards", "id", dashboard_id, {
                    "nome": nome,
                    "descricao": descricao,
                    "data_alteracao": datetime.now().isoformat(),
                    "alterado_por": current_user().get("id")
                })
                st.success("Salvo!")
                st.rerun()
        with col2:
            if st.form_submit_button("🗑️ Excluir", type="secondary", use_container_width=True):
                delete_record("dashboards", "id", dashboard_id)
                st.success("Excluído!")
                st.session_state.pagina = "dashboards"
                st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Widgets")

    fontes_tab, datasets_tab, widgets_tab = st.tabs(["Fontes", "Datasets", "Adicionar Widget"])

    with fontes_tab:
        from modules.data_sources import gerenciar_fontes
        gerenciar_fontes()

    with datasets_tab:
        datasets = listar_datasets()
        if datasets.empty:
            st.info("Nenhum dataset. Crie um abaixo:")
            with st.form("novo_dataset"):
                ds_nome = st.text_input("Nome do dataset", placeholder="Vendas por mês")
                ds_sql = st.text_area("Query SQL", placeholder="SELECT mes, SUM(vendas) FROM dados GROUP BY mes")
                if st.form_submit_button("Criar Dataset", use_container_width=True):
                    criar_dataset(ds_nome, ds_sql)
                    st.rerun()
        else:
            for _, ds in datasets.iterrows():
                st.markdown(f"**{ds['nome']}** `{ds.get('sql_query', '')[:80]}...`")

    with widgets_tab:
        # Widgets existentes com controles de posicao
        existentes = listar_widgets(dashboard_id)
        if not existentes.empty:
            st.markdown("**Widgets existentes**")
            for _, w in existentes.iterrows():
                p = parse_posicao(w)
                cols = st.columns([3, 1, 1, 1, 1])
                with cols[0]:
                    st.markdown(f"**{w['titulo']}** `{w['tipo']}` (x:{p['x']} y:{p['y']} w:{p['w']} h:{p['h']})")
                with cols[1]:
                    if st.button("⬆️", key=f"up_{w['id']}", help="Mover pra cima"):
                        novo_y = max(0, p["y"] - 1)
                        update_record("widgets", "id", w["id"], {"posicao": json.dumps({**p, "y": novo_y})})
                        st.rerun()
                with cols[2]:
                    if st.button("⬇️", key=f"down_{w['id']}", help="Mover pra baixo"):
                        novo_y = p["y"] + 1
                        update_record("widgets", "id", w["id"], {"posicao": json.dumps({**p, "y": novo_y})})
                        st.rerun()
                with cols[3]:
                    if st.button(f"{p['w']}→{min(4, p['w']+1)}", key=f"wider_{w['id']}", help="Aumentar largura"):
                        novo_w = min(4, p["w"] + 1)
                        update_record("widgets", "id", w["id"], {"posicao": json.dumps({**p, "w": novo_w})})
                        st.rerun()
                with cols[4]:
                    if st.button("🗑️", key=f"del_w_{w['id']}", help="Excluir widget"):
                        delete_record("widgets", "id", w["id"])
                        st.rerun()
            st.markdown("---")

        with st.form("novo_widget"):
            widget_cfg = editor_widget()
            c1, c2 = st.columns(2)
            with c1:
                pos_w = st.selectbox("Largura", [1, 2, 3, 4], index=1, help="1=25% 2=50% 3=75% 4=100%")
            with c2:
                pos_h = st.selectbox("Altura", [1, 2, 3], index=0)
            widget_cfg["posicao"] = {"x": 0, "y": 0, "w": pos_w, "h": pos_h}
            if st.form_submit_button("➕ Adicionar Widget", type="primary", use_container_width=True):
                if widget_cfg["titulo"]:
                    salvar_widget(dashboard_id, widget_cfg)
                    st.success("Widget adicionado!")
                    st.rerun()

    st.markdown("---")
    st.markdown("### 🎯 Pré-visualização")
    render_dashboard(dashboard_id)

def tela_dashboards():
    st.markdown(f"""
        <h1 style="color:#e8edf5">{t('dash.titulo')}</h1>
        <p style="color:#6b7fa3">{t('dash.subtitulo')}</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button(t("dash.novo"), type="primary", use_container_width=True):
            st.session_state.novo_dashboard = True

    if st.session_state.get("novo_dashboard"):
        with st.form("novo_dash_form"):
            nome = st.text_input("Nome do dashboard", placeholder="Ex: Vendas Mensais")
            desc = st.text_area("Descrição (opcional)", placeholder="O que este dashboard mostra?")
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("Criar", type="primary", use_container_width=True):
                    result = criar_dashboard(nome, desc)
                    if "error" not in result:
                        st.session_state.novo_dashboard = False
                        st.rerun()
            with c2:
                if st.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state.novo_dashboard = False
                    st.rerun()

    dashboards = listar_dashboards()
    if dashboards.empty:
        st.info(t("dash.vazio"))
        return

    cols = st.columns(3)
    for i, (_, dash) in enumerate(dashboards.iterrows()):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"""
                    <div style="background:#1a2340;padding:1rem;border-radius:12px;margin-bottom:0.5rem;border:1px solid #2a3450">
                        <h3 style="color:#e8edf5;margin:0">{dash['nome']}</h3>
                        <p style="color:#6b7fa3;font-size:0.8rem">{(dash.get('descricao') or 'Sem descrição')[:80]}</p>
                    </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👁️ Abrir", key=f"open_{dash['id']}", use_container_width=True):
                        st.session_state.dashboard_ativo = dash["id"]
                        st.session_state.pagina = "dashboard_view"
                        st.rerun()
                with c2:
                    if st.button("✏️ Editar", key=f"edit_{dash['id']}", use_container_width=True):
                        st.session_state.dashboard_ativo = dash["id"]
                        st.session_state.pagina = "dashboard_edit"
                        st.rerun()

def _exportar_dashboard(widgets: pd.DataFrame, formato: str):
    try:
        import io, csv
        dados_totais = []
        for _, w in widgets.iterrows():
            df = _carregar_dados_widget(w)
            if not df.empty:
                dados_totais.append(df)

        if not dados_totais:
            st.warning("Nenhum dado para exportar")
            return

        df_final = pd.concat(dados_totais, ignore_index=True)

        if formato == "csv":
            csv_data = df_final.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Baixar CSV",
                data=csv_data,
                file_name=f"clever_bi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv; charset=utf-8-sig",
                key=f"dl_csv_{datetime.now().timestamp()}"
            )
        elif formato == "json":
            json_data = df_final.to_json(orient="records", force_ascii=False).encode("utf-8")
            st.download_button(
                label="📥 Baixar JSON",
                data=json_data,
                file_name=f"clever_bi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key=f"dl_json_{datetime.now().timestamp()}"
            )
        elif formato == "excel":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_final.to_excel(writer, index=False, sheet_name="Dados")
            st.download_button(
                label="📥 Baixar Excel",
                data=buffer.getvalue(),
                file_name=f"clever_bi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_xlsx_{datetime.now().timestamp()}"
            )
    except Exception as e:
        st.error(f"Erro ao exportar: {e}")

def _exportar_google_sheets(widgets: pd.DataFrame, dash: dict):
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        from modules.database import current_user, get_tenant_id

        user = current_user()
        tenant_id = get_tenant_id()

        dados_totais = []
        for _, w in widgets.iterrows():
            df = _carregar_dados_widget(w)
            if not df.empty:
                dados_totais.append(df)

        if not dados_totais:
            st.warning("Nenhum dado para exportar")
            return

        df_final = pd.concat(dados_totais, ignore_index=True)
        sa_json = st.secrets.get("gcp_service_account_json")

        if not sa_json:
            st.warning("Google Sheets não configurado. Configure a chave de serviço GCP.")
            return

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(sa_json), scope)
        client = gspread.authorize(creds)

        sheet_title = f"CLEVER-BI Export {dash['nome']} {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        sh = client.create(sheet_title)
        ws = sh.get_worksheet(0)
        ws.update_title("Dados")
        ws.update([df_final.columns.values.tolist()] + df_final.values.tolist())
        sh.share(user.get("email", ""), perm_type="user", role="writer")

        st.success(f"✅ Exportado para Google Sheets: [Abrir Planilha]({sh.url})")
    except Exception as e:
        st.error(f"Erro ao exportar para Google Sheets: {e}")
