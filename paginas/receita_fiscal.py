"""Página 3: Receita Fiscal."""

import streamlit as st

from dados_receita_fiscal import (
    calcular_card_receita_total,
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

    col_card, col_grafico = st.columns([1, 3])
    with col_card:
        st.metric("Receita Total (R$) - 2027", formatar_bilhoes(calcular_card_receita_total()))
    with col_grafico:
        st.plotly_chart(construir_grafico_receita_por_categoria(), width="stretch")

    st.divider()
    st.dataframe(construir_tabela_uo_fonte(), width="stretch", hide_index=True)
