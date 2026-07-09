-- =============================================================
-- CLEVER-BI — Supabase Schema
-- Execute no SQL Editor do Supabase
-- =============================================================

-- 1. TENANTS (clientes)
CREATE TABLE IF NOT EXISTS tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nome TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  cnpj TEXT UNIQUE,
  planos TEXT[] DEFAULT '{}',
  ativo BOOLEAN DEFAULT true,
  config JSONB DEFAULT '{}',
  data_criacao TIMESTAMPTZ DEFAULT NOW(),
  criado_por UUID REFERENCES auth.users(id)
);

-- 2. USUÁRIOS (metadados, vinculado ao auth.users)
CREATE TABLE IF NOT EXISTS usuarios (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  nome TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  funcao TEXT DEFAULT 'viewer' CHECK (funcao IN ('admin','editor','viewer')),
  avatar_url TEXT,
  ativo BOOLEAN DEFAULT true,
  tema TEXT DEFAULT 'clever_dark',
  idioma TEXT DEFAULT 'pt-br',
  data_criacao TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- 3. FONTES DE DADOS
CREATE TABLE IF NOT EXISTS fontes_dados (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  nome TEXT NOT NULL,
  tipo TEXT NOT NULL CHECK (tipo IN ('supabase','google_sheets','csv','api','ftp')),
  config JSONB NOT NULL DEFAULT '{}',
  ativo BOOLEAN DEFAULT true,
  data_criacao TIMESTAMPTZ DEFAULT NOW(),
  criado_por UUID REFERENCES auth.users(id)
);
ALTER TABLE fontes_dados ENABLE ROW LEVEL SECURITY;

-- 4. CONJUNTOS DE DADOS (queries preparadas)
CREATE TABLE IF NOT EXISTS datasets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  fonte_id UUID REFERENCES fontes_dados(id),
  nome TEXT NOT NULL,
  sql_query TEXT,
  colunas JSONB DEFAULT '[]',
  cache_ttl INTEGER DEFAULT 300,
  data_criacao TIMESTAMPTZ DEFAULT NOW(),
  criado_por UUID REFERENCES auth.users(id)
);
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;

-- 5. DASHBOARDS
CREATE TABLE IF NOT EXISTS dashboards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  nome TEXT NOT NULL,
  descricao TEXT,
  layout JSONB DEFAULT '[]',
  publico BOOLEAN DEFAULT false,
  public_slug TEXT UNIQUE,
  ativo BOOLEAN DEFAULT true,
  data_criacao TIMESTAMPTZ DEFAULT NOW(),
  criado_por UUID REFERENCES auth.users(id),
  data_alteracao TIMESTAMPTZ,
  alterado_por UUID REFERENCES auth.users(id)
);
ALTER TABLE dashboards ENABLE ROW LEVEL SECURITY;

-- 6. WIDGETS
CREATE TABLE IF NOT EXISTS widgets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dashboard_id UUID REFERENCES dashboards(id) ON DELETE CASCADE NOT NULL,
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  tipo TEXT NOT NULL CHECK (tipo IN ('kpi','bar','line','pie','table','map','metric')),
  titulo TEXT NOT NULL,
  dataset_id UUID REFERENCES datasets(id),
  sql_query TEXT,
  config JSONB DEFAULT '{}',
  posicao JSONB DEFAULT '{}',
  filtros JSONB DEFAULT '[]',
  data_criacao TIMESTAMPTZ DEFAULT NOW(),
  criado_por UUID REFERENCES auth.users(id)
);
ALTER TABLE widgets ENABLE ROW LEVEL SECURITY;

-- 7. COMPARTILHAMENTO DE DASHBOARDS
CREATE TABLE IF NOT EXISTS dashboard_usuarios (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dashboard_id UUID REFERENCES dashboards(id) ON DELETE CASCADE,
  usuario_id UUID REFERENCES auth.users(id),
  permissao TEXT DEFAULT 'view' CHECK (permissao IN ('view','edit','admin')),
  data_criacao TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (dashboard_id, usuario_id)
);
ALTER TABLE dashboard_usuarios ENABLE ROW LEVEL SECURITY;

-- 8. LOG DE CONSULTAS (auditoria)
CREATE TABLE IF NOT EXISTS log_consultas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  usuario_id UUID REFERENCES auth.users(id),
  fonte_id UUID REFERENCES fontes_dados(id),
  tipo TEXT,
  query_text TEXT,
  rows_returned INTEGER,
  duration_ms INTEGER,
  data_criacao TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE log_consultas ENABLE ROW LEVEL SECURITY;

-- 9. HISTÓRICO DO CHAT IA
CREATE TABLE IF NOT EXISTS chat_ia_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  usuario_id UUID REFERENCES auth.users(id),
  pergunta TEXT NOT NULL,
  sql_gerado TEXT,
  resposta TEXT,
  dados JSONB,
  data_criacao TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE chat_ia_log ENABLE ROW LEVEL SECURITY;

-- 10. AUTOMAÇÕES (agendamento de relatórios)
CREATE TABLE IF NOT EXISTS automacoes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  nome TEXT NOT NULL,
  tipo TEXT NOT NULL CHECK (tipo IN ('email','whatsapp','webhook')),
  dashboard_id UUID REFERENCES dashboards(id),
  widget_id UUID REFERENCES widgets(id),
  config JSONB DEFAULT '{}',
  ativo BOOLEAN DEFAULT true,
  data_criacao TIMESTAMPTZ DEFAULT NOW(),
  criado_por UUID REFERENCES auth.users(id)
);
ALTER TABLE automacoes ENABLE ROW LEVEL SECURITY;

-- =============================================================
-- RLS POLICIES
-- =============================================================
-- Drop policies first to allow re-run
DROP POLICY IF EXISTS tenant_isolation ON usuarios;
DROP POLICY IF EXISTS tenant_isolation ON fontes_dados;
DROP POLICY IF EXISTS tenant_isolation ON datasets;
DROP POLICY IF EXISTS tenant_isolation ON dashboards;
DROP POLICY IF EXISTS tenant_isolation ON widgets;
DROP POLICY IF EXISTS tenant_isolation ON automacoes;
DROP POLICY IF EXISTS tenant_isolation ON log_consultas;
DROP POLICY IF EXISTS select_own ON usuarios;

-- Usuarios: cada um ve apenas a si mesmo (evita recursao nas policies)
CREATE POLICY select_own ON usuarios
  FOR SELECT
  USING (id = auth.uid());

-- Demais tabelas: isolamento por tenant via subquery segura
CREATE POLICY tenant_isolation ON fontes_dados
  USING (tenant_id = (SELECT tenant_id FROM public.usuarios WHERE id = auth.uid()));

CREATE POLICY tenant_isolation ON datasets
  USING (tenant_id = (SELECT tenant_id FROM public.usuarios WHERE id = auth.uid()));

CREATE POLICY tenant_isolation ON dashboards
  USING (tenant_id = (SELECT tenant_id FROM public.usuarios WHERE id = auth.uid()));

CREATE POLICY tenant_isolation ON widgets
  USING (tenant_id = (SELECT tenant_id FROM public.usuarios WHERE id = auth.uid()));

CREATE POLICY tenant_isolation ON automacoes
  USING (tenant_id = (SELECT tenant_id FROM public.usuarios WHERE id = auth.uid()));

CREATE POLICY tenant_isolation ON log_consultas
  USING (tenant_id = (SELECT tenant_id FROM public.usuarios WHERE id = auth.uid()));

-- =============================================================
-- FUNCTIONS
-- =============================================================

-- exec_sql: permite executar SQL arbitrário via RPC (uso interno)
CREATE OR REPLACE FUNCTION exec_sql(query_text TEXT)
RETURNS SETOF JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY EXECUTE query_text;
END;
$$;

-- register_user: cria tenant + usuário em transação atômica
CREATE OR REPLACE FUNCTION register_user(
  p_user_id UUID,
  p_email TEXT,
  p_nome TEXT,
  p_empresa TEXT
) RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_tenant_id UUID;
  v_result JSONB;
BEGIN
  -- Cria tenant
  INSERT INTO tenants (nome, slug)
  VALUES (p_empresa, lower(regexp_replace(p_empresa, '[^a-zA-Z0-9]', '-', 'g')))
  RETURNING id INTO v_tenant_id;

  -- Cria usuario
  INSERT INTO usuarios (id, tenant_id, nome, email, funcao)
  VALUES (p_user_id, v_tenant_id, p_nome, p_email, 'admin');

  v_result := jsonb_build_object(
    'tenant_id', v_tenant_id,
    'user_id', p_user_id,
    'status', 'ok'
  );
  RETURN v_result;
END;
$$;

-- insert_record: insere registro em qualquer tabela (bypass RLS)
CREATE OR REPLACE FUNCTION insert_record(
  p_table TEXT,
  p_data JSONB
) RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_result JSONB;
  v_keys TEXT[];
  v_vals TEXT[];
  v_sql TEXT;
  i INT;
BEGIN
  SELECT array_agg(key), array_agg(value::text)
  INTO v_keys, v_vals
  FROM jsonb_each_text(p_data);

  v_sql := 'INSERT INTO ' || quote_ident(p_table) || ' (' ||
    (SELECT string_agg(quote_ident(k), ', ') FROM unnest(v_keys) AS k) ||
    ') VALUES (' ||
    (SELECT string_agg('''' || replace(v, '''', '''''') || '''', ', ') FROM unnest(v_vals) AS v) ||
    ') RETURNING row_to_json(' || quote_ident(p_table) || '.*)::jsonb';

  EXECUTE v_sql INTO v_result;
  RETURN v_result;
END;
$$;

-- update_record: atualiza registro em qualquer tabela (bypass RLS)
CREATE OR REPLACE FUNCTION update_record(
  p_table TEXT,
  p_id_field TEXT,
  p_id_value TEXT,
  p_data JSONB
) RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_result JSONB;
  v_sets TEXT;
  v_sql TEXT;
  v_val TEXT;
  v_is_json BOOLEAN;
BEGIN
  SELECT string_agg(quote_ident(key) || ' = ' || (
    CASE
      WHEN value::text ~ '^-?[0-9]+\.?[0-9]*$' THEN value::text
      WHEN value::text ~ '^true|false$' THEN value::text
      WHEN value::text ~ '^null$' THEN 'NULL'
      WHEN value::text ~ '^\{.*\}$' OR value::text ~ '^\[.*\]$' THEN value::text
      ELSE '''' || replace(value::text, '''', '''''') || ''''
    END
  ), ', ')
  INTO v_sets
  FROM jsonb_each(p_data);

  v_sql := 'UPDATE ' || quote_ident(p_table) ||
    ' SET ' || v_sets ||
    ' WHERE ' || quote_ident(p_id_field) || ' = ''' || replace(p_id_value, '''', '''''') || '''' ||
    ' RETURNING row_to_json(' || quote_ident(p_table) || '.*)::jsonb';

  EXECUTE v_sql INTO v_result;
  RETURN v_result;
END;
$$;

-- delete_record: deleta registro em qualquer tabela (bypass RLS)
CREATE OR REPLACE FUNCTION delete_record(
  p_table TEXT,
  p_id_field TEXT,
  p_id_value TEXT
) RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_sql TEXT;
BEGIN
  v_sql := 'DELETE FROM ' || quote_ident(p_table) ||
    ' WHERE ' || quote_ident(p_id_field) || ' = ''' || replace(p_id_value, '''', '''''') || '''';
  EXECUTE v_sql;
  RETURN FOUND;
END;
$$;

-- =============================================================
-- REMOVER trigger automático de signup (causa conflito)
-- O registro é gerenciado pelo código da aplicação
-- =============================================================
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS handle_new_user;
