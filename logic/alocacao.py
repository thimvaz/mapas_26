def alocar(fila_a, fila_b, salas):
    # Mantenha o código existente que já está aqui...
    mapas = {}
    a = list(fila_a)
    b = list(fila_b)
    
    alocados_corretos = 0
    quebras_regra = 0

    for _, sala in salas.iterrows():
        nome = sala["sala"]
        linhas = int(sala["fileiras"])
        colunas = int(sala["colunas"])

        mapa = [[None]*colunas for _ in range(linhas)]

        if len(a) >= len(b):
            pares, impares = a, b
        else:
            pares, impares = b, a

        for c in range(colunas):
            fila_preferencial = pares if c % 2 == 0 else impares
            fila_secundaria = impares if c % 2 == 0 else pares

            for l in range(linhas):
                if fila_preferencial:
                    aluno = fila_preferencial.pop(0)
                    aluno["quebra_regra"] = False
                    mapa[l][c] = aluno
                    alocados_corretos += 1
                elif fila_secundaria:
                    aluno = fila_secundaria.pop(0)
                    aluno["quebra_regra"] = True
                    mapa[l][c] = aluno
                    quebras_regra += 1

        mapas[nome] = mapa
        
        if not a and not b:
            break

    return mapas, len(a), len(b), alocados_corretos, quebras_regra


def alocar_terceirao(filas_por_turma, salas):
    """
    Lógica exclusiva para distribuir várias turmas da mesma série numa sala.
    """
    mapas = {}
    alocados_corretos = 0
    quebras_regra = 0

    # Cria uma lista apenas com as turmas que ainda têm alunos (Ex: ['A', 'B', 'C'])
    turmas = [t for t in filas_por_turma if len(filas_por_turma[t]) > 0]

    for _, sala in salas.iterrows():
        nome = sala["sala"]
        linhas = int(sala["fileiras"])
        colunas = int(sala["colunas"])

        mapa = [[None]*colunas for _ in range(linhas)]

        if not turmas:
            break

        # A turma com MAIS ALUNOS ganha a coluna 0 para escoar mais rápido
        turmas.sort(key=lambda t: len(filas_por_turma[t]), reverse=True)

        for c in range(colunas):
            # Alterna as turmas nas colunas (0->Turma 1, 1->Turma 2, 2->Turma 3, 3->Turma 1...)
            turma_preferencial = turmas[c % len(turmas)]
            
            for l in range(linhas):
                if filas_por_turma[turma_preferencial]:
                    aluno = filas_por_turma[turma_preferencial].pop(0)
                    aluno["quebra_regra"] = False
                    mapa[l][c] = aluno
                    alocados_corretos += 1
                else:
                    # Se esta turma acabou no meio da coluna, procura outra para não deixar cadeira vazia
                    alocado = False
                    for outra_turma in turmas:
                        if filas_por_turma[outra_turma]:
                            aluno = filas_por_turma[outra_turma].pop(0)
                            aluno["quebra_regra"] = True # Sinaliza no visual
                            mapa[l][c] = aluno
                            quebras_regra += 1
                            alocado = True
                            break
                    if not alocado:
                        pass # Acabaram todos os alunos de todas as turmas

        mapas[nome] = mapa
        # Remove as turmas que esvaziaram antes de ir para a próxima sala
        turmas = [t for t in turmas if len(filas_por_turma[t]) > 0]

    sobras_totais = sum(len(f) for f in filas_por_turma.values())
    return mapas, sobras_totais, alocados_corretos, quebras_regra
