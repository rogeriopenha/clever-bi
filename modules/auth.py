import streamlit as st
import hashlib
from modules.database import get_supabase, insert_record, query_native

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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # INCLUSÃO DO LOGO VETORIAL COMPATÍVEL COM TEMA CLARO E ESCURO
        st.markdown("""
            <div style="text-align:center; padding:1rem 0 2rem 0; max-width:100%;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 200" width="100%" style="max-width:320px; height:auto;">
                  <defs>
                    <linearGradient id="metalBlue" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#0077B6" />
                      <stop offset="100%" stop-color="#00B4D8" />
                    </linearGradient>
                    <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#FFFFFF" />
                      <stop offset="100%" stop-color="#E2E8F0" />
                    </linearGradient>
                  </defs>
                  <g transform="translate(40, 40)">
                    <path d="M 70 20 A 50 50 0 1 0 70 120" fill="none" stroke="url(#metalBlue)" stroke-width="14" stroke-linecap="round"/>
                    <rect x="45" y="75" width="10" height="25" rx="4" fill="#0077B6" />
                    <rect x="62" y="55" width="10" height="45" rx="4" fill="#00B4D8" />
                    <rect x="79" y="30" width="10" height="70" rx="4" fill="url(#metalBlue)" />
                    <circle cx="84" cy="30" r="8" fill="#00F5D4" />
                  </g>
                  <text x="180" y="115" font-family="'Montserrat', 'Segoe UI', sans-serif" font-size="54" font-weight="800" fill="url(#textGrad)" letter-spacing="2">CLEVER</text>
                  <line x1="435" y1="73" x2="435" y2="115" stroke="#CBD5E1" stroke-width="3" stroke-linecap="round" />
                  <text x="455" y="112" font-family="'Montserrat', 'Segoe UI', sans-serif" font-size="42" font-weight="300" fill="#00B4D8" letter-spacing="4">BI</text>
                  <g transform="translate(515, 75) scale(0.8)">
                    <circle cx="10" cy="10" r="9" fill="none" stroke="#00B4D8" stroke-width="1.5"/>
                    <path d="M 7 14 L 7 6 L 11 6 C 13 6, 14 7, 14 8.5 C 14 10, 13 11, 11 11 L 9 11 L 9 14 M 9 9 L 11 9 C 11.5 9, 12 8.8, 12 8.5 C 12 8.2, 11.5 8, 11 8 L 9 8 Z M 11 11 L 13.5 14" fill="none" stroke="#00B4D8" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
                  </g>
                </svg>
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