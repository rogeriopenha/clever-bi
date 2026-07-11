import os
import base64
import streamlit as st
import hashlib
from modules.database import get_supabase, insert_record, query_native

_AUTH_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fazer_login(email: str, senha: str) -> bool:
    sb = get_supabase()
    if sb:
        try:
            resp = sb.auth.sign_in_with_password({"email": email, "password": senha})
            if resp.user:
                st.session_state.supabase_client = sb
                user_data = query_native("usuarios", filters={"email": email})
                if not user_data.empty:
                    row = user_data.iloc[0]
                    st.session_state.user = row.to_dict()
                    st.session_state.tenant_id = row["tenant_id"]
                    st.session_state.tema = row.get("tema", "clever_dark")
                    st.session_state.idioma = row.get("idioma", "pt-br")
                    st.session_state.logged_in = True
                    return True
                st.error("Usuário autenticado mas sem perfil. Contate o admin.")
                return False
        except Exception as e:
            st.error(f"Erro no login: {e}")
            return False
    return _login_local(email, senha)

def _login_local(email: str, senha: str) -> bool:
    usuarios = {
        "admin@clever.com": {"senha": "admin123", "nome": "Admin", "funcao": "admin", "tenant_id": "local"},
        "demo@clever.com": {"senha": "demo123", "nome": "Demo", "funcao": "viewer", "tenant_id": "local"},
    }
    if email in usuarios and senha == usuarios[email]["senha"]:
        st.session_state.user = {
            "id": email,
            "email": email,
            "nome": usuarios[email]["nome"],
            "funcao": usuarios[email]["funcao"],
            "tenant_id": usuarios[email]["tenant_id"]
        }
        st.session_state.tenant_id = usuarios[email]["tenant_id"]
        st.session_state.logged_in = True
        return True
    return False

def fazer_logout():
    sb = get_supabase()
    if sb:
        try:
            sb.auth.sign_out()
        except Exception:
            pass
    for key in ["user", "tenant_id", "logged_in", "pagina", "supabase_client", "tema", "idioma"]:
        st.session_state.pop(key, None)
    st.rerun()

def registrar(email: str, senha: str, nome: str, empresa: str) -> bool:
    sb = get_supabase()
    if not sb:
        st.warning("Modo offline: registro apenas via admin")
        return False
    try:
        resp = sb.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {"data": {"full_name": nome, "company": empresa}}
        })
        if resp.user:
            result = sb.rpc("register_user", {
                "p_user_id": resp.user.id,
                "p_email": email,
                "p_nome": nome,
                "p_empresa": empresa
            }).execute()
            if result.data:
                st.session_state.supabase_client = sb
                return True
            st.error("Erro ao criar perfil de usuário")
            return False
    except Exception as e:
        st.error(f"Erro no registro: {e}")
    return False

def login_screen():
    st.markdown("""
        <style>
        section[data-testid="stAppViewContainer"] {
            background: #f1f5f9;
        }
        </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with open(os.path.join(_AUTH_ROOT, "Logo-CleverBI.svg"), "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode("utf-8")
        _login_logo = f'<img src="data:image/svg+xml;base64,{_b64}" style="height:36px;width:auto">'
        st.markdown(f"""
            <div style="text-align:center;padding:1.5rem 0">
                {_login_logo}
            </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("### Entrar")
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("E-mail", placeholder="seu@email.com", key="login_email")
                senha = st.text_input("Senha", type="password", placeholder="••••••", key="login_senha")
                if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                    if fazer_login(email, senha):
                        st.rerun()
                    else:
                        st.error("E-mail ou senha inválidos")

            st.markdown("""
                <p style="color:#6b7fa3;font-size:0.85rem;text-align:center">
                    Demo: <strong>demo@clever.com</strong> / <strong>demo123</strong>
                </p>
            """, unsafe_allow_html=True)

            with st.expander("Criar nova conta"):
                with st.form("register_form"):
                    nome = st.text_input("Nome completo", placeholder="Seu nome")
                    email_r = st.text_input("E-mail", placeholder="seu@email.com")
                    empresa = st.text_input("Empresa", placeholder="Nome da empresa")
                    senha_r = st.text_input("Senha", type="password", placeholder="••••••")
                    senha_r2 = st.text_input("Confirmar senha", type="password", placeholder="••••••")
                    if st.form_submit_button("Criar conta", use_container_width=True):
                        if senha_r != senha_r2:
                            st.error("Senhas não conferem")
                        elif not nome or not email_r or not empresa:
                            st.error("Preencha todos os campos")
                        elif registrar(email_r, senha_r, nome, empresa):
                            st.success("Conta criada! Verifique seu e-mail para confirmar.")

def verificar_login():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_screen()
        return None
    return st.session_state.user
