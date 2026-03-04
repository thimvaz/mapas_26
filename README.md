# 🏫 Gerador de Mapas de Provas - Web App

## 📌 Sobre o Projeto
O **Gerador de Mapas de Provas** é uma aplicação web desenvolvida para automatizar e otimizar a distribuição de alunos em salas de avaliação. Criado para resolver o desafio logístico de ensalamento escolar, o sistema substitui processos manuais em planilhas por um algoritmo inteligente e uma interface em nuvem, poupando dezenas de horas de trabalho da equipa de coordenação pedagógica.

## 🚀 Principais Funcionalidades

* **Integração Cloud (Single Source of Truth):** O banco de dados da aplicação consome informações em tempo real do Google Sheets, garantindo que a gestão de alunos, transferências e layouts de salas estejam sempre atualizados sem necessidade de alterar o código.
* **Motor Antifraude (Intercalamento):** O algoritmo de alocação utiliza uma lógica de *Round-Robin* para intercalar alunos de séries diferentes (ou de turmas diferentes, no caso do 3º Ano do Ensino Médio). O sistema garante matematicamente que alunos da mesma turma nunca se sentem lado a lado ou um atrás do outro.
* **Gestão de Inclusão (Salas Flex):** Separação automática de alunos que necessitam de atendimento adaptado, alocando-os em "Salas Flex" designadas pela coordenação no momento da geração do mapa.
* **Privacidade e Proteção de Dados:** Geração de "Listas de Pátio" limpas, sem rótulos de inclusão ou flexibilização, protegendo a privacidade dos estudantes. O sistema também possui uma camada de autenticação via senha nativa no Streamlit para restringir o acesso à aplicação.
* **Exportação Completa (Excel):** Geração de planilhas prontas para impressão contendo:
  * Lista do Pátio (Ordem alfabética).
  * Lista de Assinaturas (Ordenada pela disposição física das carteiras, puxando RM e Número de Chamada).
  * Mapas Visuais (Matriz de carteiras por sala).
  * Relatórios de Alerta (Sobras de vagas e alunos de aplicação individual/inclusão).

## 🛠️ Tecnologias Utilizadas
* **Python** (Lógica de roteamento e manipulação de dados)
* **Pandas** (Engenharia de dados e estruturação das matrizes de ensalamento)
* **Streamlit** (Desenvolvimento da interface Web UI e Deploy Contínuo)
* **Google Cloud Platform (GCP) & Gspread** (Comunicação segura via Service Accounts com a API do Google Sheets)
* **Openpyxl** (Geração e formatação de relatórios em Excel via BytesIO)

## 💡 O Desafio do "Terceirão" (Atualização 2026)
Um dos maiores desafios lógicos desta versão foi adaptar a heurística de alocação para o 3º Ano do Ensino Médio, que passou de 2 para 3 turmas simultâneas. Foi desenvolvido um motor de alocação exclusivo que cria múltiplos agrupamentos e faz o intercalamento perfeito em colunas, cruzando 3 turmas dentro das mesmas salas.

---
*Desenvolvido por **Thiago Vaz** | Professor de Física e Robótica, e estudante de Data Science.*
