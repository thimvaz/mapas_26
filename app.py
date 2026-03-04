import streamlit as st
import pandas as pd

# ===== SISTEMA DE SENHA =====
def checar_senha():
    def senha_inserida():
        if st.session_state["senha_digitada"] == st.secrets["senha_acesso"]:
            st.session_state["senha_correta"] = True
            del st.session_state["senha_digitada"]
        else:
            st.session_state["senha_correta"] = False

    if "senha_correta" not in st.session_state:
        st.text_input("🔐 Digite a senha para acessar o Gerador de Mapas:", type="password", on_change=senha_inserida, key="senha_digitada")
        return False
    elif not st.session_state["senha_correta"]:
        st.text_input("🔐 Digite a senha para acessar o Gerador de Mapas:", type="password", on_change=senha_inserida, key="senha_digitada")
        st.error("😕 Senha incorreta. Tente novamente.")
        return False
    else:
        return True

if not checar_senha():
    st.stop()

# ===== FUNÇÃO PARA IDENTIFICAR QUEM FICOU DE FORA =====
def calcular_sobras(df_selecionados, mapas):
    """Cruza a lista de alunos selecionados com quem realmente foi alocado nos mapas."""
    alocados = set()
    for mapa in mapas.values():
        for linha in mapa:
            for aluno in linha:
                if aluno:
                    alocados.add(f"{aluno.get('nome', '')}_{aluno.get('turma', '')}")
    
    # Cria uma cópia para não mexer no dataframe original
    df_verificacao = df_selecionados.copy()
    df_verificacao["chave"] = df_verificacao["nome"] + "_" + df_verificacao["turma"]
    
    # Filtra os alunos que NÃO estão no set de alocados e tira os "Ausentes"
    df_sobras = df_verificacao[
        (~df_verificacao["chave"].isin(alocados)) & 
        (df_verificacao["Status"] != "Ausente")
    ].drop(columns=["chave"])
    
    return df_sobras

# ============================
from services.sheets import carregar_planilha
from logic.round_robin import preparar_fila_round_robin, preparar_filas_por_turma
from logic.alocacao import alocar, alocar_terceirao
from ui.layout import render_layout
from ui.mapas import exibir_mapa, exibir_listas_patio, exibir_listas_assinaturas
from ui.export import exportar_excel
from ui.selecao_alunos import selecionar_alunos

# SUAS CHAVES AQUI
ID_ALUNOS = "1ku2R7umGREP6foZC8Qk-46bEsB9QD2_fAUH18IcRYrc"
ID_SALAS = "1BF8ENESt0jQurf_5pDeDJbk0Y3Vns90Qsrsc8lRi0ZE"

df_alunos = carregar_planilha(ID_ALUNOS)
df_salas = carregar_planilha(ID_SALAS, "salas")
df_turma_sala = carregar_planilha(ID_SALAS, "turma_sala")

s1, s2, is_terceirao, salas_flex, gerar = render_layout(df_alunos, df_salas, df_turma_sala)

# ===== VIA A: LÓGICA DO TERCEIRÃO =====
if is_terceirao:
    df_s1 = df_alunos[df_alunos["serie"] == s1]
    
    st.markdown(f"### 🎓 Modo Especial: {s1}")
    alunos_s1_editados = selecionar_alunos(df_s1, "Alunos (Todas as turmas)")

    if gerar:
        with st.spinner("A processar heurística por turmas (Terceirão)..."):
            s1_regulares = alunos_s1_editados[alunos_s1_editados["Status"] == "Regular"]
            s1_flex = alunos_s1_editados[alunos_s1_editados["Status"] == "Flex"]

            filas_reg = preparar_filas_por_turma(pd.DataFrame(s1_regulares))
            filas_flx = preparar_filas_por_turma(pd.DataFrame(s1_flex))

            salas_alvo_nomes = df_turma_sala[df_turma_sala["serie"] == s1]["sala"].unique()
            salas_alvo_df = df_salas[(df_salas["sala"].isin(salas_alvo_nomes)) & (df_salas["ativa"] == 1)]
            
            df_salas_regulares = salas_alvo_df[~salas_alvo_df["sala"].isin(salas_flex)].sort_values(by="sala")
            df_salas_flex = salas_alvo_df[salas_alvo_df["sala"].isin(salas_flex)].sort_values(by="sala")

            mapas_reg, sob_reg, ok_reg, qb_reg = alocar_terceirao(filas_reg, df_salas_regulares)
            mapas_flx, sob_flx, ok_flx, qb_flx = alocar_terceirao(filas_flx, df_salas_flex)

            st.markdown("---")
            st.markdown("### 🎯 Resultado da Alocação Regular")
            r1, r2, r3 = st.columns(3)
            r1.metric("Alocação Perfeita", ok_reg)
            r2.metric("Quebras de Padrão ⚠️", qb_reg, delta_color="inverse")
            r3.metric("Sobras", sob_reg, delta_color="inverse" if sob_reg > 0 else "off")

            if len(s1_flex) > 0:
                st.markdown("### ♿ Resultado da Alocação Flex")
                f1, f2, f3 = st.columns(3)
                f1.metric("Alocação Perfeita", ok_flx)
                f2.metric("Quebras de Padrão", qb_flx, delta_color="off")
                f3.metric("Sobras", sob_flx, delta_color="inverse" if sob_flx > 0 else "off")

            mapas_completos = {**mapas_reg}
            for nome_sala, mapa in mapas_flx.items():
                mapas_completos[f"{nome_sala} (FLEX)"] = mapa

            # CÁLCULO DAS SOBRAS REAIS
            df_lista_sobras = calcular_sobras(alunos_s1_editados, mapas_completos)
            
            if not df_lista_sobras.empty:
                st.error(f"🚨 ALERTA: {len(df_lista_sobras)} aluno(s) ficaram sem carteira por falta de espaço físico!")
                st.dataframe(df_lista_sobras[["serie", "turma", "nome", "Status"]].reset_index(drop=True), use_container_width=True)

            st.download_button(
                label="📥 Baixar Planilha para Impressão",
                data=exportar_excel(mapas_completos, df_lista_sobras),
                file_name=f"Mapas_{s1}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

            st.markdown("---")
            exibir_listas_patio(mapas_completos)
            exibir_listas_assinaturas(mapas_completos)

            st.markdown("---")
            st.markdown("### 🗺️ Mapas Regulares")
            for nome, mapa in mapas_reg.items():
                exibir_mapa(nome, mapa)
            if mapas_flx:
                st.markdown("### 🗺️ Mapas Flex")
                for nome, mapa in mapas_flx.items():
                    exibir_mapa(f"{nome} (FLEX)", mapa)

# ===== VIA B: LÓGICA NORMAL (Duas Séries) =====
elif s1 and s2 and s1 != s2:
    df_s1 = df_alunos[df_alunos["serie"] == s1]
    df_s2 = df_alunos[df_alunos["serie"] == s2]

    col1, col2 = st.columns(2)
    with col1:
        alunos_s1_editados = selecionar_alunos(df_s1, f"Série {s1}")
    with col2:
        alunos_s2_editados = selecionar_alunos(df_s2, f"Série {s2}")

    if gerar:
        with st.spinner("A processar heurística em duas vias..."):
            s1_regulares = alunos_s1_editados[alunos_s1_editados["Status"] == "Regular"]
            s2_regulares = alunos_s2_editados[alunos_s2_editados["Status"] == "Regular"]
            
            s1_flex = alunos_s1_editados[alunos_s1_editados["Status"] == "Flex"]
            s2_flex = alunos_s2_editados[alunos_s2_editados["Status"] == "Flex"]

            fila_s1_reg = preparar_fila_round_robin(pd.DataFrame(s1_regulares))
            fila_s2_reg = preparar_fila_round_robin(pd.DataFrame(s2_regulares))
            fila_s1_flex = preparar_fila_round_robin(pd.DataFrame(s1_flex))
            fila_s2_flex = preparar_fila_round_robin(pd.DataFrame(s2_flex))

            salas_alvo_nomes = df_turma_sala[df_turma_sala["serie"].isin([s1, s2])]["sala"].unique()
            salas_alvo_df = df_salas[(df_salas["sala"].isin(salas_alvo_nomes)) & (df_salas["ativa"] == 1)]
            
            df_salas_regulares = salas_alvo_df[~salas_alvo_df["sala"].isin(salas_flex)].sort_values(by="sala")
            df_salas_flex = salas_alvo_df[salas_alvo_df["sala"].isin(salas_flex)].sort_values(by="sala")

            mapas_reg, sob1_reg, sob2_reg, ok_reg, qb_reg = alocar(fila_s1_reg, fila_s2_reg, df_salas_regulares)
            mapas_flx, sob1_flx, sob2_flx, ok_flx, qb_flx = alocar(fila_s1_flex, fila_s2_flex, df_salas_flex)

            st.markdown("---")
            st.markdown("### 🎯 Resultado da Alocação Regular")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Alocação Perfeita", ok_reg)
            r2.metric("Quebras de Regra ⚠️", qb_reg, delta_color="inverse")
            r3.metric(f"Sobras ({s1})", sob1_reg, delta_color="inverse" if sob1_reg > 0 else "off")
            r4.metric(f"Sobras ({s2})", sob2_reg, delta_color="inverse" if sob2_reg > 0 else "off")

            if len(s1_flex) > 0 or len(s2_flex) > 0:
                st.markdown("### ♿ Resultado da Alocação Flex")
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("Alocação Perfeita", ok_flx)
                f2.metric("Quebras de Regra", qb_flx, delta_color="off")
                f3.metric(f"Sobras ({s1})", sob1_flx, delta_color="inverse" if sob1_flx > 0 else "off")
                f4.metric(f"Sobras ({s2})", sob2_flx, delta_color="inverse" if sob2_flx > 0 else "off")

            mapas_completos = {**mapas_reg}
            for nome_sala, mapa in mapas_flx.items():
                mapas_completos[f"{nome_sala} (FLEX)"] = mapa

            # CÁLCULO DAS SOBRAS REAIS
            df_todos_alunos = pd.concat([alunos_s1_editados, alunos_s2_editados])
            df_lista_sobras = calcular_sobras(df_todos_alunos, mapas_completos)

            if not df_lista_sobras.empty:
                st.error(f"🚨 ALERTA: {len(df_lista_sobras)} aluno(s) ficaram sem carteira por falta de espaço físico!")
                st.dataframe(df_lista_sobras[["serie", "turma", "nome", "Status"]].reset_index(drop=True), use_container_width=True)

            st.download_button(
                label="📥 Baixar Planilha para Impressão",
                data=exportar_excel(mapas_completos, df_lista_sobras),
                file_name=f"Mapas_{s1}_{s2}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

            st.markdown("---")
            exibir_listas_patio(mapas_completos)
            exibir_listas_assinaturas(mapas_completos)

            st.markdown("---")
            st.markdown("### 🗺️ Mapas Regulares")
            for nome, mapa in mapas_reg.items():
                exibir_mapa(nome, mapa)
            if mapas_flx:
                st.markdown("### 🗺️ Mapas Flex")
                for nome, mapa in mapas_flx.items():
                    exibir_mapa(f"{nome} (FLEX)", mapa)
