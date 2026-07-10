import streamlit as st
import pandas as pd
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

def tela_automacao():
    st.markdown("### 🤖 Automação — Manipulação de Arquivos")
    st.markdown("Gerencie arquivos via FTP, renomeie, mova, exclua e processe automaticamente.")

    tab_ftp, tab_local, tab_regras = st.tabs(["📡 FTP/SFTP", "📁 Arquivos Locais", "⚙️ Regras Automáticas"])

    with tab_ftp:
        st.markdown("**Conexão FTP**")
        with st.form("ftp_form"):
            c1, c2 = st.columns(2)
            with c1:
                host = st.text_input("Host", placeholder="ftp.copastur.com.br")
                port = st.number_input("Porta", value=21, min_value=1, max_value=65535)
                user = st.text_input("Usuário")
            with c2:
                protocolo = st.selectbox("Protocolo", ["FTP", "SFTP"])
                password = st.text_input("Senha", type="password")
                remote_path = st.text_input("Diretório remoto", value="/", placeholder="/arquivos/proceda")

            conectado = st.form_submit_button("🔌 Conectar", type="primary")

        if conectado:
            with st.spinner("Conectando..."):
                try:
                    if protocolo == "FTP":
                        from ftplib import FTP
                        ftp = FTP(host)
                        ftp.login(user, password)
                        ftp.cwd(remote_path)
                        arquivos = []
                        ftp.retrlines("LIST", lambda x: arquivos.append(x))
                        ftp.quit()
                        st.session_state.ftp_conexao = {"host": host, "user": user, "password": password,
                                                         "path": remote_path, "protocolo": protocolo}
                        st.success(f"✅ Conectado! {len(arquivos)} itens encontrados")

                        if arquivos:
                            df_ftp = pd.DataFrame(arquivos, columns=["Listagem"])
                            st.dataframe(df_ftp, use_container_width=True)
                    else:
                        try:
                            import paramiko
                            ssh = paramiko.SSHClient()
                            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            ssh.connect(host, port=port, username=user, password=password)
                            sftp = ssh.open_sftp()
                            sftp.chdir(remote_path)
                            arquivos = sftp.listdir_attr(".")
                            sftp.close()
                            ssh.close()
                            st.session_state.ftp_conexao = {"host": host, "user": user, "password": password,
                                                             "path": remote_path, "protocolo": protocolo}
                            st.success(f"✅ Conectado! {len(arquivos)} itens")

                            df_sftp = pd.DataFrame([{
                                "nome": a.filename,
                                "tamanho": a.st_size,
                                "modificado": datetime.fromtimestamp(a.st_mtime) if a.st_mtime else None,
                                "tipo": "DIR" if a.st_mode and (a.st_mode & 0o40000) else "FILE"
                            } for a in arquivos])
                            st.dataframe(df_sftp, use_container_width=True)
                        except ImportError:
                            st.warning("Biblioteca paramiko não instalada. Instale com: pip install paramiko")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")

        if "ftp_conexao" in st.session_state:
            st.markdown("---")
            st.markdown("**Operações FTP**")
            op = st.selectbox("Ação", ["Listar diretório", "Baixar arquivo", "Enviar arquivo",
                                       "Renomear", "Mover", "Excluir", "Criar diretório"])

            if op == "Listar diretório":
                subdir = st.text_input("Subdiretório (opcional)", key="ftp_ls_dir")
                if st.button("Listar", key="ftp_ls_go"):
                    st.info(f"Listando: {st.session_state.ftp_conexao['path']}/{subdir}")

            elif op == "Baixar arquivo":
                nome_arquivo = st.text_input("Nome do arquivo remoto", key="ftp_get_file")
                destino = st.text_input("Destino local", value="./downloads", key="ftp_get_dest")
                if st.button("📥 Baixar", key="ftp_get_go"):
                    Path(destino).mkdir(parents=True, exist_ok=True)
                    try:
                        if st.session_state.ftp_conexao["protocolo"] == "FTP":
                            from ftplib import FTP
                            ftp = FTP(st.session_state.ftp_conexao["host"])
                            ftp.login(st.session_state.ftp_conexao["user"],
                                      st.session_state.ftp_conexao["password"])
                            ftp.cwd(st.session_state.ftp_conexao["path"])
                            with open(Path(destino) / nome_arquivo, "wb") as f:
                                ftp.retrbinary(f"RETR {nome_arquivo}", f.write)
                            ftp.quit()
                        st.success(f"✅ Baixado para {destino}/{nome_arquivo}")
                    except Exception as e:
                        st.error(f"Erro: {e}")

            elif op == "Enviar arquivo":
                uploaded = st.file_uploader("Selecionar arquivo local", key="ftp_put_file")
                nome_remoto = st.text_input("Nome remoto (opcional)", key="ftp_put_name")
                if uploaded and st.button("📤 Enviar", key="ftp_put_go"):
                    nome_final = nome_remoto or uploaded.name
                    try:
                        if st.session_state.ftp_conexao["protocolo"] == "FTP":
                            from ftplib import FTP
                            ftp = FTP(st.session_state.ftp_conexao["host"])
                            ftp.login(st.session_state.ftp_conexao["user"],
                                      st.session_state.ftp_conexao["password"])
                            ftp.cwd(st.session_state.ftp_conexao["path"])
                            ftp.storbinary(f"STOR {nome_final}", uploaded)
                            ftp.quit()
                        st.success(f"✅ Enviado: {nome_final}")
                    except Exception as e:
                        st.error(f"Erro: {e}")

            elif op == "Renomear":
                old = st.text_input("Nome atual", key="ftp_rename_old")
                new = st.text_input("Novo nome", key="ftp_rename_new")
                if st.button("✏️ Renomear", key="ftp_rename_go"):
                    try:
                        if st.session_state.ftp_conexao["protocolo"] == "FTP":
                            from ftplib import FTP
                            ftp = FTP(st.session_state.ftp_conexao["host"])
                            ftp.login(st.session_state.ftp_conexao["user"],
                                      st.session_state.ftp_conexao["password"])
                            ftp.cwd(st.session_state.ftp_conexao["path"])
                            ftp.rename(old, new)
                            ftp.quit()
                        st.success(f"✅ Renomeado: {old} → {new}")
                    except Exception as e:
                        st.error(f"Erro: {e}")

            elif op == "Mover":
                src = st.text_input("Arquivo origem", key="ftp_mv_src")
                dst = st.text_input("Diretório destino", key="ftp_mv_dst")
                if st.button("📦 Mover", key="ftp_mv_go"):
                    try:
                        if st.session_state.ftp_conexao["protocolo"] == "FTP":
                            from ftplib import FTP
                            ftp = FTP(st.session_state.ftp_conexao["host"])
                            ftp.login(st.session_state.ftp_conexao["user"],
                                      st.session_state.ftp_conexao["password"])
                            ftp.cwd(st.session_state.ftp_conexao["path"])
                            ftp.rename(src, f"{dst}/{src}")
                            ftp.quit()
                        st.success(f"✅ Movido: {src} → {dst}")
                    except Exception as e:
                        st.error(f"Erro: {e}")

            elif op == "Excluir":
                target = st.text_input("Arquivo/diretório a excluir", key="ftp_del_target")
                if st.button("🗑️ Excluir", key="ftp_del_go"):
                    if st.checkbox("Confirmar exclusão?", key="ftp_del_confirm"):
                        try:
                            if st.session_state.ftp_conexao["protocolo"] == "FTP":
                                from ftplib import FTP
                                ftp = FTP(st.session_state.ftp_conexao["host"])
                                ftp.login(st.session_state.ftp_conexao["user"],
                                          st.session_state.ftp_conexao["password"])
                                ftp.cwd(st.session_state.ftp_conexao["path"])
                                ftp.delete(target)
                                ftp.quit()
                            st.success(f"✅ Excluído: {target}")
                        except Exception as e:
                            st.error(f"Erro: {e}")

            elif op == "Criar diretório":
                new_dir = st.text_input("Nome do diretório", key="ftp_mkdir_name")
                if st.button("📁 Criar", key="ftp_mkdir_go"):
                    try:
                        if st.session_state.ftp_conexao["protocolo"] == "FTP":
                            from ftplib import FTP
                            ftp = FTP(st.session_state.ftp_conexao["host"])
                            ftp.login(st.session_state.ftp_conexao["user"],
                                      st.session_state.ftp_conexao["password"])
                            ftp.cwd(st.session_state.ftp_conexao["path"])
                            ftp.mkd(new_dir)
                            ftp.quit()
                        st.success(f"✅ Diretório criado: {new_dir}")
                    except Exception as e:
                        st.error(f"Erro: {e}")

    with tab_local:
        st.markdown("**📁 Gerenciador de Arquivos Locais**")
        diretorio = st.text_input("Diretório", value=".", key="fs_dir")
        if st.button("📂 Listar", key="fs_ls"):
            path = Path(diretorio)
            if path.exists():
                itens = []
                for p in path.iterdir():
                    itens.append({
                        "nome": p.name,
                        "tipo": "DIR" if p.is_dir() else "FILE",
                        "tamanho_kb": round(p.stat().st_size / 1024, 1) if p.is_file() else 0,
                        "modificado": datetime.fromtimestamp(p.stat().st_mtime)
                    })
                df_fs = pd.DataFrame(itens)
                st.dataframe(df_fs, use_container_width=True)

                # Operações
                op_local = st.selectbox("Operação", ["Renomear", "Mover", "Copiar", "Excluir"])
                alvo = st.text_input("Arquivo/diretório alvo", key="fs_target")
                if op_local == "Renomear":
                    novo_nome = st.text_input("Novo nome", key="fs_rename_new")
                    if st.button("✏️ Executar", key="fs_rename_go"):
                        (path / alvo).rename(path / novo_nome)
                        st.success(f"Renomeado para {novo_nome}")
                        st.rerun()
                elif op_local == "Mover":
                    destino_mv = st.text_input("Diretório destino", key="fs_mv_dest")
                    if st.button("📦 Executar", key="fs_mv_go"):
                        shutil.move(str(path / alvo), destino_mv)
                        st.success(f"Movido para {destino_mv}")
                elif op_local == "Copiar":
                    destino_cp = st.text_input("Diretório destino", key="fs_cp_dest")
                    if st.button("📋 Executar", key="fs_cp_go"):
                        if (path / alvo).is_dir():
                            shutil.copytree(str(path / alvo), str(Path(destino_cp) / alvo))
                        else:
                            shutil.copy2(str(path / alvo), destino_cp)
                        st.success(f"Copiado para {destino_cp}")
                elif op_local == "Excluir":
                    if st.checkbox("Confirmar exclusão", key="fs_del_confirm"):
                        if st.button("🗑️ Executar", key="fs_del_go"):
                            target = path / alvo
                            if target.is_dir():
                                shutil.rmtree(target)
                            else:
                                target.unlink()
                            st.success(f"Excluído: {alvo}")
                            st.rerun()

    with tab_regras:
        st.markdown("**⚙️ Regras de Automação**")
        st.markdown("Defina regras para processamento automático de arquivos.")

        with st.form("regra_form"):
            nome_regra = st.text_input("Nome da regra", placeholder="Ex: Processar Proceda Diário")
            fonte = st.selectbox("Fonte", ["FTP", "Diretório Local", "Proceda (ocoren)", "Proceda (conemb)", "Proceda (doccob)"])
            padrao = st.text_input("Padrão de arquivo (glob)", placeholder="*.csv, *.txt, proceda_*.csv",
                                   help="Ex: *.csv ou ocorrencia_*.txt")

            st.markdown("**Ação ao encontrar:**")
            acao = st.selectbox("Ação", [
                "Baixar e processar", "Mover para processado",
                "Renomear com data", "Excluir após ler",
                "Carregar como Dataset", "Executar ETL"
            ])

            destino_arquivo = st.text_input("Diretório de destino/processados",
                                            placeholder="./processados", value="./processados")

            if st.form_submit_button("💾 Salvar Regra", type="primary"):
                regras = st.session_state.get("automacao_regras", [])
                regras.append({
                    "nome": nome_regra,
                    "fonte": fonte,
                    "padrao": padrao,
                    "acao": acao,
                    "destino": destino_arquivo,
                    "criada": datetime.now().isoformat()
                })
                st.session_state.automacao_regras = regras
                st.success(f"Regra '{nome_regra}' salva!")
                st.rerun()

        # Listar regras salvas
        regras = st.session_state.get("automacao_regras", [])
        if regras:
            st.markdown("---")
            st.markdown("**Regras cadastradas:**")
            for i, r in enumerate(regras):
                with st.expander(f"{r['nome']} ({r['fonte']} → {r['acao']})"):
                    st.json(r)
                    if st.button(f"🗑️ Excluir regra", key=f"del_regra_{i}"):
                        regras.pop(i)
                        st.session_state.automacao_regras = regras
                        st.rerun()
                    if st.button(f"▶️ Executar agora", key=f"run_regra_{i}"):
                        st.info(f"Regra '{r['nome']}' executada! (simulado)")
        else:
            st.info("Nenhuma regra cadastrada ainda.")
