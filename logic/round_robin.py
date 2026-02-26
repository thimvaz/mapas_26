import pandas as pd

def preparar_fila_round_robin(df):
    # Apenas embaralha os alunos
    df = df.sample(frac=1).reset_index(drop=True)

    filas = []
    grupos = {
        t: df[df["turma"] == t].to_dict("records")
        for t in df["turma"].unique()
    }

    while any(grupos.values()):
        for t in grupos:
            if grupos[t]:
                filas.append(grupos[t].pop(0))

    return filas

def preparar_filas_por_turma(df):
    """
    Retorna um dicionário com os alunos separados por turma e embaralhados.
    Usado exclusivamente para a alocação especial do Terceirão.
    """
    df = df.sample(frac=1).reset_index(drop=True)
    
    grupos = {
        t: df[df["turma"] == t].to_dict("records")
        for t in df["turma"].unique()
    }
    return grupos
