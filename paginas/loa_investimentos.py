"""Página 6: LOA Investimentos."""

import html

import pandas as pd
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
.tabela-investimentos-wrapper {
    max-height: 480px;
    overflow-y: auto;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.tabela-investimentos {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.85rem;
    background: #ffffff;
}
.tabela-investimentos th {
    position: sticky;
    top: 0;
    z-index: 1;
    text-align: left;
    background: #eef1f4;
    padding: 0.6rem 0.9rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: #616e7c;
    box-shadow: inset 0 -1px 0 #cbd2d9;
    overflow: auto;
    resize: horizontal;
    min-width: 70px;
}
.tabela-investimentos th:nth-child(1) { width: 18%; }
.tabela-investimentos th:nth-child(2) { width: 62%; }
.tabela-investimentos th:nth-child(3) { width: 20%; }
.tabela-investimentos td {
    padding: 0.5rem 0.9rem;
    border-top: 1px solid #eef1f4;
    white-space: normal;
    overflow-wrap: break-word;
    word-break: break-word;
}
.tabela-investimentos td:last-child {
    text-align: right;
    font-weight: 600;
}
.tabela-investimentos tbody tr:hover {
    background: #fafbfc;
}
</style>
"""

_CHAVE_FILTRO_UO = "loa_investimentos_filtro_uo"


def renderizar() -> None:
    st.title("LOA Investimentos")
    st.markdown(_CSS_PAGINA, unsafe_allow_html=True)

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
    _renderizar_tabela(construir_tabela(base_despesa))


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


def _renderizar_tabela(tabela: pd.DataFrame) -> None:
    """Tabela em HTML (em vez de st.dataframe) para permitir ao usuário
    redimensionar as colunas (arrastando a borda) com quebra de linha
    dinâmica do texto, algo que o grid nativo do st.dataframe não oferece.
    """
    colunas = list(tabela.columns)
    cabecalho = "".join(f"<th>{html.escape(coluna)}</th>" for coluna in colunas)

    linhas_html = []
    for _, linha in tabela.iterrows():
        celulas = "".join(f"<td>{html.escape(str(linha[coluna]))}</td>" for coluna in colunas)
        linhas_html.append(f"<tr>{celulas}</tr>")

    st.markdown(
        f"""
        <div class="tabela-investimentos-wrapper">
          <table class="tabela-investimentos">
            <thead><tr>{cabecalho}</tr></thead>
            <tbody>{''.join(linhas_html)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
