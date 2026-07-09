"""
Setup inicial: cria tenant e usuários demo no Supabase.
"""
import psycopg2
import sys
from supabase import create_client

URL = "https://rfdypszfljyxbbkeozpp.supabase.co"
ANON_KEY = "sb_publishable_wadUn-EC8XJNZCudmisq8A_gON-X4-t"
DB_URL = "db.rfdypszfljyxbbkeozpp.supabase.co"
PASSWORD = "WA92YS7TAF4Ruf5x"

sb = create_client(URL, ANON_KEY)

def sql(query):
    conn = psycopg2.connect(
        host=DB_URL, port=5432, dbname="postgres",
        user="postgres", password=PASSWORD, sslmode="require"
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(query)
        try:
            return cur.fetchall()
        except:
            return []
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("=== Setup CLEVER-BI Demo ===\n")

    # 1. Tenant
    print("[1] Criando tenant 'Minha Empresa'...")
    rows = sql("SELECT id FROM tenants WHERE slug = 'minha-empresa'")
    if rows:
        tenant_id = rows[0][0]
        print(f"  [OK] Tenant ja existe: {tenant_id}")
    else:
        sql("INSERT INTO tenants (nome, slug) VALUES ('Minha Empresa', 'minha-empresa')")
        tenant_id = sql("SELECT id FROM tenants WHERE slug = 'minha-empresa'")[0][0]
        print(f"  [OK] Tenant criado: {tenant_id}")

    # 2. Usuários
    usuarios = [
        ("demo@clever.com", "demo123", "Usuário Demo", "admin"),
        ("admin@clever.com", "admin123", "Admin", "admin"),
    ]

    for email, senha, nome, funcao in usuarios:
        print(f"\n[2] Processando {email}...")
        uid = None

        try:
            resp = sb.auth.sign_up({"email": email, "password": senha})
            if resp.user:
                uid = resp.user.id
                print(f"  [OK] Auth user criado: {uid}")
        except Exception as e:
            if "already registered" in str(e).lower():
                print(f"  [~] Ja registrado no auth")
            else:
                print(f"  [~] Auth signup: {e}")

        if not uid:
            rows = sql(f"SELECT id FROM auth.users WHERE email = '{email}'")
            if rows:
                uid = rows[0][0]
                print(f"  [OK] ID do auth: {uid}")

        if not uid:
            print(f"  [ERR] Nao foi possivel obter/criar usuario")
            continue

        rows = sql(f"SELECT id FROM usuarios WHERE email = '{email}'")
        if rows:
            print(f"  [OK] Perfil ja existe: {rows[0][0]}")
        else:
            sql(f"""
                INSERT INTO usuarios (id, tenant_id, nome, email, funcao)
                VALUES ('{uid}', '{tenant_id}', '{nome}', '{email}', '{funcao}')
            """)
            print(f"  [OK] Perfil criado: {nome} ({funcao})")

    print("\n=== Setup concluido! ===")
    print("Login: demo@clever.com / demo123")
    print("Se o login falhar, confirme o email no Supabase Dashboard:")
    print("-> Authentication -> Users -> confirme manualmente os usuarios")
    print("Ou desative: Authentication -> Settings -> Confirm email = OFF")
