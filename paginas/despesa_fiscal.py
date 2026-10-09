"""Página 4: Despesa Fiscal."""

import streamlit as st

from dados_despesa_fiscal import (
    calcular_card_despesa_total,
    construir_grafico_despesa_por_funcao,
    construir_grafico_despesa_por_grupo,
    construir_grafico_despesa_por_poder,
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
    st.title("Despesa Fiscal")
    st.markdown(_CSS_CARD_CENTRALIZADO, unsafe_allow_html=True)

    col_card, col_grafico = st.columns([1, 3])
    with col_card:
        st.metric("Despesa Total (R$) - 2027", formatar_bilhoes(calcular_card_despesa_total()))
    with col_grafico:
        st.plotly_chart(construir_grafico_despesa_por_poder(), width="stretch")

    st.plotly_chart(construir_grafico_despesa_por_grupo(), width="stretch")
    st.plotly_chart(construir_grafico_despesa_por_funcao(), width="stretch")
