import pandas as pd
import io

def exportar_excel(mapas):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        
        # BLINDAGEM: Se não houver mapas, cria uma aba de aviso para o Excel não quebrar
        if not mapas:
            df_vazio = pd.DataFrame([["Nenhuma sala foi mapeada para estas séries. Verifique a aba 'turma_sala'."]])
            df_vazio.to_excel(writer, sheet_name="Aviso", index=False, header=False)
            output.seek(0)
            return output

        # 1. Criar a aba de Lista de Alunos (Para afixar no Pátio)
        dados_lista = []
        for sala, mapa in mapas.items():
            for linha in mapa:
                for aluno in linha:
                    if aluno:
                        dados_lista.append({
                            "Série": str(aluno.get("serie", "")),
                            "Turma": str(aluno.get("turma", "")),
                            "Nome": str(aluno.get("nome", "")),
                            "Sala de Prova": sala
                        })
        
        if dados_lista:
            df_lista = pd.DataFrame(dados_lista)
            # Ordena alfabeticamente para facilitar a procura pelos alunos
            df_lista.sort_values(by=["Série", "Turma", "Nome"], inplace=True)
            df_lista.to_excel(writer, sheet_name="Lista do Pátio", index=False)

        # 2. Gerar as abas dos Mapas (Para os professores nas salas)
        for sala, mapa in mapas.items():
            matriz_excel = []
            for linha in mapa:
                linha_excel = []
                for a in linha:
                    if a:
                        # Formata o texto da célula com quebra de linha (Ex: João\n(3EM A))
                        texto = f"{a.get('nome', '')}\n({a.get('serie', '')} {a.get('turma', '')})"
                        linha_excel.append(texto)
                    else:
                        linha_excel.append("")
                matriz_excel.append(linha_excel)

            df_mapa = pd.DataFrame(matriz_excel)
            # O Excel tem um limite de 31 caracteres para o nome da aba
            df_mapa.to_excel(writer, sheet_name=sala[:31], index=False, header=False)

    output.seek(0)
    return output
