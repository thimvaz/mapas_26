import pandas as pd
import io

def exportar_excel(mapas):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        
        if not mapas:
            df_vazio = pd.DataFrame([["Nenhuma sala foi mapeada para estas séries. Verifique a aba 'turma_sala'."]])
            df_vazio.to_excel(writer, sheet_name="Aviso", index=False, header=False)
            output.seek(0)
            return output

        # 1. Criar a aba de Lista de Alunos (Para afixar no Pátio) - SEM ESTIGMA
        dados_lista = []
        for sala, mapa in mapas.items():
            # Remove o rótulo (FLEX) do nome da sala para as listas públicas
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

        # 2. Criar a aba de Lista de Assinaturas (Para o professor na sala) - SEM ESTIGMA
        dados_assinaturas = []
        for sala, mapa in mapas.items():
            sala_limpa = sala.replace(" (FLEX)", "")
            
            for linha in mapa:
                for aluno in linha:
                    if aluno:
                        dados_assinaturas.append({
                            "Sala": sala_limpa,
                            "Série/Turma": f"{aluno.get('serie', '')} {aluno.get('turma', '')}",
                            "Nome": str(aluno.get("nome", "")),
                            "RM": str(aluno.get("rm", "")),
                            "Nº": str(aluno.get("numero", "")),
                            "Assinatura": "" 
                        })
        
        if dados_assinaturas:
            df_assinaturas = pd.DataFrame(dados_assinaturas)
            df_assinaturas.to_excel(writer, sheet_name="Lista de Assinaturas", index=False)

        # 3. Gerar as abas dos Mapas Visuais (Uso interno da equipa)
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
