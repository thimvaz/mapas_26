import streamlit as st

def render_layout(df_alunos, df_salas, df_turma_sala):
    st.title("📝 Gerador de Mapas de Provas")

    series = sorted(df_alunos["serie"].astype(str).unique())

    st.sidebar.header("Configuração de Séries")
    s1 = st.sidebar.selectbox("Série 1", series, index=0)
    
    # Deteta se é o Terceirão (Se o nome for diferente de "3EM" na sua base, ajuste aqui)
    is_terceirao = (s1 == "3EM")
    
    index_s2 = 1 if len(series) > 1 else 0
    s2 = st.sidebar.selectbox("Série 2", series, index=index_s2, disabled=is_terceirao)

    # Se for terceirão, a série alvo é só a primeira. Senão, são ambas.
    series_alvo = [str(s1)] if is_terceirao else [str(s1), str(s2)]
    
    salas_alvo = df_turma_sala[df_turma_sala["serie"].astype(str).isin(series_alvo)]["sala"].unique()
    salas_ativas = df_salas[df_salas["ativa"] == 1]["sala"].unique()
    salas_disponiveis = sorted([sala for sala in salas_alvo if sala in salas_ativas])

    st.sidebar.markdown("---")
    st.sidebar.header("Configuração Flex")
    salas_flex = st.sidebar.multiselect(
        "Selecione as Salas Flex:",
        salas_disponiveis,
        help="Estas salas serão retiradas do mapeamento regular e preenchidas APENAS com alunos marcados como 'Flex'."
    )

    st.sidebar.markdown("---")
    gerar = st.sidebar.button("Gerar mapas")

    # Devolvemos a variável "is_terceirao" para o app.py saber o que fazer
    return s1, s2, is_terceirao, salas_flex, gerar
