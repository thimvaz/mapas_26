import streamlit as st
import pandas as pd

def selecionar_alunos(df, titulo):
    st.subheader(titulo)

    # 1. Preparar a coluna de Status inicial
    if "Status" not in df.columns:
        if "flex" in df.columns:
            df["Status"] = df["flex"].apply(lambda x: "Flex" if x == 1 else "Regular")
        else:
            df["Status"] = "Regular"

    # 2. Criar um DataFrame focado apenas no que importa para a tela
    df_visao = df[["RM", "nome", "turma", "Status"]].copy()

    # 3. O componente mágico: Data Editor
    df_editado = st.data_editor(
        df_visao,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Local de Prova",
                help="Escolha onde o aluno fará a prova",
                width="medium",
                options=["Regular", "Flex", "Ausente"],
                required=True,
            ),
            "nome": st.column_config.TextColumn("Nome do Aluno", disabled=True),
            "turma": st.column_config.TextColumn("Turma", disabled=True),
            "RM": st.column_config.TextColumn("RM", disabled=True),
        },
        hide_index=True,
        use_container_width=True,
        key=f"editor_{titulo}"
    )

    # 4. Devolver o DataFrame original inteiro, mas com o Status atualizado
    df_final = df.copy()
    df_final["Status"] = df_editado["Status"].values

    return df_final
