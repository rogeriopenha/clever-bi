import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

SUPABASE_AVAILABLE = False

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    pass

def get_supabase() -> object:
    if "supabase_client" in st.session_state:
        return st.session_state.supabase_client
    url = st.secrets.get("supabase_url", "")
    key = st.secrets.get("supabase_key", "")
    if url and key and SUPABASE_AVAILABLE:
        client = create_client(url, key)
        st.session_state.supabase_client = client
        return client
    return None

def is_offline() -> bool:
    return st.secrets.get("modo_offline", False)

def query_supabase(sql: str, params: dict = None) -> pd.DataFrame:
    sb = get_supabase()
    if sb:
        try:
            resp = sb.rpc("exec_sql", {"query_text": sql}).execute()
            return pd.DataFrame(resp.data)
        except Exception:
            pass
    return pd.DataFrame()

def query_native(table: str, select: str = "*", filters: dict = None) -> pd.DataFrame:
    sb = get_supabase()
    if not sb:
        return pd.DataFrame()
    try:
        query = sb.table(table).select(select)
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)
        resp = query.execute()
        return pd.DataFrame(resp.data)
    except Exception as e:
        st.error(f"Erro ao consultar {table}: {e}")
        return pd.DataFrame()

def insert_record(table: str, data: dict) -> dict:
    sb = get_supabase()
    if not sb:
        return {"error": "Supabase não configurado"}
    try:
        # Converte valores dict para JSON string (para colunas JSONB)
        dados_rpc = {}
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                dados_rpc[k] = json.dumps(v)
            else:
                dados_rpc[k] = v
        resp = sb.rpc("insert_record", {
            "p_table": table,
            "p_data": dados_rpc
        }).execute()
        if resp.data:
            return resp.data[0] if isinstance(resp.data, list) else resp.data
        return {"error": "Sem retorno"}
    except Exception as e:
        return {"error": str(e)}

def update_record(table: str, id_field: str, id_value, data: dict) -> dict:
    sb = get_supabase()
    if not sb:
        return {"error": "Supabase não configurado"}
    try:
        resp = sb.table(table).update(data).eq(id_field, id_value).execute()
        if resp.data:
            return resp.data[0]
        return {"error": "Sem retorno"}
    except Exception as e:
        return {"error": str(e)}

def delete_record(table: str, id_field: str, id_value) -> bool:
    sb = get_supabase()
    if not sb:
        return False
    try:
        sb.table(table).delete().eq(id_field, id_value).execute()
        return True
    except Exception:
        return False

def get_tenant_id() -> str:
    return st.session_state.get("tenant_id", "")

def current_user() -> dict:
    return st.session_state.get("user", {})

def log_query(tenant_id: str, usuario_id: str, tipo: str, query_text: str, rows: int, ms: int):
    insert_record("log_consultas", {
        "tenant_id": tenant_id,
        "usuario_id": usuario_id,
        "tipo": tipo,
        "query_text": query_text[:500],
        "rows_returned": rows,
        "duration_ms": ms
    })

def load_csv(uploaded_file) -> pd.DataFrame:
    try:
        return pd.read_csv(uploaded_file)
    except Exception:
        try:
            return pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            return pd.DataFrame()
