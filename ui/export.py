import pandas as pd
import io

def exportar_excel(mapas, df_sobras=None):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        
        if not mapas:
            df_vazio = pd.DataFrame([["Nenhuma sala foi mapeada para estas séries. Verifique a aba 'turma_sala'."]])
            df_vazio.to_excel(writer, sheet_name="Aviso", index=False, header=False)
            output.seek(0)
            return output

        if df_sobras is not None and not df_sobras.empty:
            df_sobras_export = df_sobras[["serie", "turma", "nome", "Status"]].rename(
                columns={"serie": "Série", "turma": "Turma", "nome": "Nome"}
            )
            df_sobras_export.to_excel(writer, sheet_name="ALERTA - Sobras", index=False)

        # 1. Lista do Pátio
        dados_lista = []
        for sala, mapa in mapas.items():
            sala_limpa = sala.replace(" (FLEX)", "")
            for linha in mapa:
                for aluno in linha:
                    if aluno:
                        dados_lista.append({
                            "Série": str(aluno.get("serie", "")),
                            "Turma": str(aluno.get("turma", "")),
                            "Nome": str(aluno.get("nome", "")),
                            "Sala de Prova": sala_limpa
                        })
        
        if dados_lista:
            df_lista = pd.DataFrame(dados_lista)
            df_lista.sort_values(by=["Série", "Turma", "Nome"], inplace=True)
            df_lista.to_excel(writer, sheet_name="Lista do Pátio", index=False)

        # 2. Lista de Assinaturas (Puxando RM e "chamada")
        dados_assinaturas = []
        for sala, mapa in mapas.items():
            sala_limpa = sala.replace(" (FLEX)", "")
            for linha in mapa:
                for aluno in linha:
                    if aluno:
                        rm_aluno = str(aluno.get("RM", aluno.get("rm", "")))
                        num_aluno = str(aluno.get("chamada", aluno.get("Chamada", "")))
                        
                        # Limpa o decimal caso o Pandas leia como float (ex: 4524.0 -> 4524)
                        if num_aluno.endswith('.0'):
                            num_aluno = num_aluno[:-2]
                        if rm_aluno.endswith('.0'):
                            rm_aluno = rm_aluno[:-2]

                        dados_assinaturas.append({
                            "Sala": sala_limpa,
                            "Série/Turma": f"{aluno.get('serie', '')} {aluno.get('turma', '')}",
                            "Nome": str(aluno.get("nome", "")),
                            "RM": rm_aluno,
                            "Nº": num_aluno,
                            "Assinatura": "" 
                        })
        
        if dados_assinaturas:
            df_assinaturas = pd.DataFrame(dados_assinaturas)
            df_assinaturas.to_excel(writer, sheet_name="Lista de Assinaturas", index=False)

        # 3. Mapas Visuais
        for sala, mapa in mapas.items():
            matriz_excel = []
            for linha in mapa:
                linha_excel = []
                for a in linha:
                    if a:
                        texto = f"{a.get('nome', '')}\n({a.get('serie', '')} {a.get('turma', '')})"
                        linha_excel.append(texto)
                    else:
                        linha_excel.append("")
                matriz_excel.append(linha_excel)

            df_mapa = pd.DataFrame(matriz_excel)
            df_mapa.to_excel(writer, sheet_name=sala[:31], index=False, header=False)

    output.seek(0)
    return output
