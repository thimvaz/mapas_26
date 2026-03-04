import streamlit as st
import pandas as pd

def exibir_mapa(nome, mapa):
    st.subheader(f"Sala {nome}")

    html = "<table style='border-collapse:collapse; margin-bottom: 20px;'>"
    for linha in mapa:
        html += "<tr>"
        for aluno in linha:
            if aluno:
                cor_fundo = "#ffebee" if aluno.get("quebra_regra") else "transparent"
                alerta = " ⚠️" if aluno.get("quebra_regra") else ""
                
                nome_completo = aluno.get('nome', '')
                info_aluno = f"<strong>{nome_completo}</strong><br><small>{aluno.get('serie', '')} {aluno.get('turma', '')}</small>"
                
                html += f"<td style='border:1px solid #333;padding:8px;text-align:center;background-color:{cor_fundo}'>{info_aluno}{alerta}</td>"
            else:
                html += "<td style='border:1px solid #ccc;padding:8px;background-color:#f9f9f9;width:120px;'></td>"
        html += "</tr>"
    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)


def exibir_listas_patio(mapas):
    dados = []
    for sala, mapa in mapas.items():
        sala_limpa = sala.replace(" (FLEX)", "")
        for linha in mapa:
            for aluno in linha:
                if aluno:
                    dados.append({
                        "Série": str(aluno.get("serie", "")),
                        "Turma": str(aluno.get("turma", "")),
                        "Nome": str(aluno.get("nome", "")),
                        "Sala": sala_limpa
                    })
    
    if not dados:
        return

    df_lista = pd.DataFrame(dados)
    df_lista.sort_values(by=["Série", "Turma", "Nome"], inplace=True)

    agrupamentos = df_lista.groupby(["Série", "Turma"])

    st.markdown("### 📋 Listas de Ensalamento (Para o Pátio)")
    
    for (serie, turma), df_grupo in agrupamentos:
        with st.expander(f"Lista: {serie} - Turma {turma}"):
            st.dataframe(
                df_grupo[["Nome", "Sala"]].reset_index(drop=True),
                use_container_width=True
            )

def exibir_listas_assinaturas(mapas):
    dados = []
    for sala, mapa in mapas.items():
        sala_limpa = sala.replace(" (FLEX)", "")
        for linha in mapa:
            for aluno in linha:
                if aluno:
                    rm_aluno = str(aluno.get("RM", aluno.get("rm", "")))
                    num_aluno = str(aluno.get("chamada", aluno.get("Chamada", "")))
                    
                    if num_aluno.endswith('.0'):
                        num_aluno = num_aluno[:-2]
                    if rm_aluno.endswith('.0'):
                        rm_aluno = rm_aluno[:-2]
                    
                    dados.append({
                        "Sala": sala_limpa,
                        "Série/Turma": f"{aluno.get('serie', '')} {aluno.get('turma', '')}",
                        "Nome": str(aluno.get("nome", "")),
                        "RM": rm_aluno,
                        "Nº": num_aluno,
                        "Assinatura": ""
                    })
    
    if not dados:
        return

    df_assinaturas = pd.DataFrame(dados)
    agrupamentos = df_assinaturas.groupby("Sala", sort=False)

    st.markdown("### ✍️ Listas de Assinaturas (Por Sala)")
    
    for sala, df_grupo in agrupamentos:
        with st.expander(f"Assinaturas: Sala {sala}"):
            st.dataframe(
                df_grupo[["Série/Turma", "Nome", "RM", "Nº", "Assinatura"]].reset_index(drop=True),
                use_container_width=True
            )
