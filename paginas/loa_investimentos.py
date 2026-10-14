"""Página 6: LOA Investimentos."""

import streamlit as st

from dados_loa_investimentos import (
    calcular_card_despesa_total,
    calcular_card_receita_total,
    construir_base_despesa,
    construir_base_receita,
    construir_lista_uo,
    construir_tabela,
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

_CHAVE_FILTRO_UO = "loa_investimentos_filtro_uo"


def renderizar() -> None:
    st.title("LOA Investimentos")
    st.markdown(_CSS_CARDS_CENTRALIZADOS, unsafe_allow_html=True)

    base_receita = construir_base_receita()
    base_despesa = construir_base_despesa()
    uo_selecionadas = _renderizar_filtro()

    if uo_selecionadas:
        base_receita = base_receita[base_receita["uo_label"].isin(uo_selecionadas)]
        base_despesa = base_despesa[base_despesa["uo_label"].isin(uo_selecionadas)]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Receita Total (R$) - 2027",
            formatar_bilhoes(calcular_card_receita_total(base_receita)),
        )
    with col2:
        st.metric(
            "Despesa Total (R$) - 2027",
            formatar_bilhoes(calcular_card_despesa_total(base_despesa)),
        )

    st.divider()
    st.dataframe(construir_tabela(base_despesa), width="stretch", hide_index=True)


def _renderizar_filtro() -> list[str]:
    col1, col2 = st.columns([3, 1])
    with col1:
        uos = st.multiselect("Unidade Orçamentária", construir_lista_uo(), key=_CHAVE_FILTRO_UO)
    with col2:
        st.write("")
        st.button("Limpar filtros", on_click=_limpar_filtro)
    return uos


def _limpar_filtro() -> None:
    st.session_state[_CHAVE_FILTRO_UO] = []
