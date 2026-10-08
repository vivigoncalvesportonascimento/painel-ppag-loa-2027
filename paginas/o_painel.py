"""Página 1: explicação do que consiste o painel."""

import streamlit as st


def renderizar() -> None:
    st.title("O Painel")

    st.markdown(
        """
**O que é a ferramenta:** Consiste num painel criado pela Subsecretaria de
Planeamento e Orçamento (SPLOR) que agrega informações relativas ao PPAG
2024-2027 (com revisão para 2027) e à Lei Orçamentária Anual (LOA) de 2027.

**Finalidade:** O seu objetivo principal é proporcionar aos cidadãos uma
forma mais visual, dinâmica e prática de aceder e interagir com os dados do
orçamento do Estado de Minas Gerais, através da utilização de tabelas, mapas
e gráficos.

**Componentes do Sistema de Planeamento e Orçamento:**
"""
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(
            "**PMDI**\n\n"
            "Plano Mineiro de Desenvolvimento Integrado: planeamento "
            "estratégico de longo prazo focado em criar condições para o "
            "desenvolvimento sustentável do estado."
        )
    with col2:
        st.info(
            "**PPAG**\n\n"
            "Plano Plurianual de Ação Governamental: estipula as metas, "
            "ações e programas da administração estadual com uma duração "
            "de quatro anos."
        )
    with col3:
        st.info(
            "**LDO**\n\n"
            "Lei de Diretrizes Orçamentárias: funciona como uma ponte de "
            "ligação entre o PPAG e a LOA, regulando a elaboração do "
            "orçamento e fixando as prioridades para o ano seguinte."
        )
    with col4:
        st.info(
            "**LOA**\n\n"
            "Lei Orçamentária Anual: tem como função prever as receitas e "
            "estabelecer os limites de despesas para o próximo ano "
            "financeiro."
        )
