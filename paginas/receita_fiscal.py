"""Página 3: Receita Fiscal."""

import streamlit as st

from dados_receita_fiscal import (
    calcular_card_receita_total,
    construir_base_enriquecida,
    construir_grafico_receita_por_categoria,
    construir_tabela_uo_fonte,
)
from utils import formatar_bilhoes

_CSS_CARD_CENTRALIZADO = """
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
    st.title("Receita Fiscal")
    st.markdown(_CSS_CARD_CENTRALIZADO, unsafe_allow_html=True)

    area_card_grafico = st.container()

    base = construir_base_enriquecida()
    base_filtrada = _renderizar_filtros(base)

    with area_card_grafico:
        col_card, col_grafico = st.columns([1, 3])
        with col_card:
            st.metric(
                "Receita Total (R$) - 2027",
                formatar_bilhoes(calcular_card_receita_total(base_filtrada)),
            )
        with col_grafico:
            st.plotly_chart(
                construir_grafico_receita_por_categoria(base_filtrada), width="stretch"
            )

    st.dataframe(construir_tabela_uo_fonte(base_filtrada), width="stretch", hide_index=True)


def _renderizar_filtros(base):
    col1, col2 = st.columns(2)
    with col1:
        uos = st.multiselect("UO", sorted(base["UO"].unique()))
    with col2:
        fontes = st.multiselect(
            "Fonte de Recursos", sorted(base["fonte_de_recursos"].unique())
        )

    base_filtrada = base
    if uos:
        base_filtrada = base_filtrada[base_filtrada["UO"].isin(uos)]
    if fontes:
        base_filtrada = base_filtrada[base_filtrada["fonte_de_recursos"].isin(fontes)]
    return base_filtrada
