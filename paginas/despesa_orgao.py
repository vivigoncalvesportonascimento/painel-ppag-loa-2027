"""Página 5: Despesa por Órgão."""

import html

import streamlit as st

from dados_despesa_orgao import (
    calcular_card_despesa_total,
    construir_base_enriquecida,
    construir_grafico_despesa_por_grupo,
    construir_lista_acao,
    construir_lista_fonte,
)
from utils import formatar_bilhoes

_CSS_PAGINA = """
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
.lista-cartao {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    padding: 0.9rem 1.1rem;
    height: 360px;
    overflow-y: auto;
}
.lista-cartao h4 {
    margin: 0 0 0.5rem;
    font-size: 0.95rem;
    color: #1f2933;
}
.lista-cartao .item {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.5rem;
    padding: 0.5rem 0;
    border-top: 1px solid #eef1f4;
}
.lista-cartao .item:first-of-type {
    border-top: none;
}
.lista-cartao .item .label {
    font-size: 0.82rem;
    color: #1f2933;
}
.lista-cartao .item .valor {
    font-size: 0.9rem;
    font-weight: 700;
    color: #0047AB;
    white-space: nowrap;
}
</style>
"""

_CHAVE_FILTRO_UO = "despesa_orgao_filtro_uo"


def renderizar() -> None:
    st.title("Despesa por Órgão")
    st.markdown(_CSS_PAGINA, unsafe_allow_html=True)

    base = construir_base_enriquecida()
    base_filtrada = _renderizar_filtro(base)

    col_card, col_grafico = st.columns([1, 3])
    with col_card:
        st.metric(
            "Despesa Total (R$) - 2027",
            formatar_bilhoes(calcular_card_despesa_total(base_filtrada)),
        )
    with col_grafico:
        st.plotly_chart(construir_grafico_despesa_por_grupo(base_filtrada), width="stretch")

    col_acao, col_fonte = st.columns(2)
    with col_acao:
        _renderizar_lista_cartao("Despesa por Ação Orçamentária", construir_lista_acao(base_filtrada))
    with col_fonte:
        _renderizar_lista_cartao("Despesa por Fonte de Recursos", construir_lista_fonte(base_filtrada))


def _renderizar_filtro(base):
    col1, col2 = st.columns([3, 1])
    with col1:
        uos = st.multiselect(
            "Unidade Orçamentária", sorted(base["uo_label"].unique()), key=_CHAVE_FILTRO_UO
        )
    with col2:
        st.write("")
        st.button("Limpar filtros", on_click=_limpar_filtro)

    if uos:
        return base[base["uo_label"].isin(uos)]
    return base


def _limpar_filtro() -> None:
    st.session_state[_CHAVE_FILTRO_UO] = []


def _renderizar_lista_cartao(titulo: str, itens: list[dict]) -> None:
    linhas_html = "".join(
        f'<div class="item"><div class="label">{html.escape(item["label"])}</div>'
        f'<div class="valor">{html.escape(item["valor"])}</div></div>'
        for item in itens
    )
    st.markdown(
        f'<div class="lista-cartao"><h4>{html.escape(titulo)}</h4>{linhas_html}</div>',
        unsafe_allow_html=True,
    )
