"""Página 2: dados gerais do orçamento 2027."""

import streamlit as st

from dados_visao_geral import (
    calcular_cards,
    construir_grafico_area_tematica,
    construir_grafico_setor_governo,
)
from utils import formatar_bilhoes

_CSS_CARDS_CENTRALIZADOS = """
<style>
[data-testid="stMetric"] {
    text-align: center;
}
[data-testid="stMetric"] [data-testid="stMetricLabel"] {
    justify-content: center;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    justify-content: center;
}
</style>
"""


def renderizar() -> None:
    st.title("Visão Geral")
    st.caption("Dados gerais do orçamento 2027")
    st.markdown(_CSS_CARDS_CENTRALIZADOS, unsafe_allow_html=True)

    _renderizar_cards()
    st.divider()
    _renderizar_graficos()


def _renderizar_cards() -> None:
    cards = calcular_cards()
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Previsão 2027 - Orçamento Fiscal",
            formatar_bilhoes(cards["total_fiscal"]),
        )
    with col2:
        st.metric(
            "Previsão 2027 - Orçamento de Investimentos",
            formatar_bilhoes(cards["total_investimento"]),
        )
    with col3:
        st.metric("Quantidade de Programas", cards["qtd_programas"])
    with col4:
        st.metric("Quantidade de Ações", cards["qtd_acoes"])
    with col5:
        st.metric("Projetos Estratégicos", cards["qtd_projetos_estrategicos"])


def _renderizar_graficos() -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(construir_grafico_area_tematica(), width="stretch")
    with col2:
        st.plotly_chart(construir_grafico_setor_governo(), width="stretch")
