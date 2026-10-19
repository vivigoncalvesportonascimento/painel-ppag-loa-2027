"""Página 8: Regionalização."""

import html

import pandas as pd
import streamlit as st

from dados_regionalizacao import (
    construir_base_enriquecida,
    construir_listas_filtro,
    construir_mapa,
    construir_tabela,
)
from exportacao import botoes_exportar_tabela

_CSS_PAGINA = """
<style>
.tabela-regionalizacao-wrapper {
    max-height: 480px;
    overflow-y: auto;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.tabela-regionalizacao {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.82rem;
    background: #ffffff;
}
.tabela-regionalizacao th {
    position: sticky;
    top: 0;
    z-index: 1;
    text-align: left;
    background: #eef1f4;
    padding: 0.55rem 0.75rem;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: #616e7c;
    box-shadow: inset 0 -1px 0 #cbd2d9;
    overflow: auto;
    resize: horizontal;
    min-width: 70px;
}
.tabela-regionalizacao th:nth-child(1) { width: 20%; }
.tabela-regionalizacao th:nth-child(2) { width: 14%; }
.tabela-regionalizacao th:nth-child(3) { width: 10%; }
.tabela-regionalizacao th:nth-child(4) { width: 14%; }
.tabela-regionalizacao th:nth-child(5) { width: 14%; }
.tabela-regionalizacao th:nth-child(6) { width: 12%; }
.tabela-regionalizacao th:nth-child(7) { width: 16%; }
.tabela-regionalizacao td {
    padding: 0.45rem 0.75rem;
    border-top: 1px solid #eef1f4;
    white-space: normal;
    overflow-wrap: break-word;
    word-break: break-word;
}
.tabela-regionalizacao td:last-child,
.tabela-regionalizacao td:nth-last-child(2) {
    text-align: right;
    font-weight: 600;
}
.tabela-regionalizacao tbody tr:hover {
    background: #fafbfc;
}
</style>
"""

_CHAVES_FILTRO = {
    "uo": "regionalizacao_filtro_uo",
    "acao": "regionalizacao_filtro_acao",
    "regiao": "regionalizacao_filtro_regiao",
    "municipio": "regionalizacao_filtro_municipio",
    "produto": "regionalizacao_filtro_produto",
}


def renderizar() -> None:
    st.title("Regionalização")
    st.markdown(_CSS_PAGINA, unsafe_allow_html=True)

    base = construir_base_enriquecida()
    filtros = _renderizar_filtros(base)

    base_sem_municipio = _aplicar_filtros(base, filtros, ignorar_municipio=True)
    base_tabela = _aplicar_filtros(base, filtros, ignorar_municipio=False)

    st.plotly_chart(
        construir_mapa(base_sem_municipio, filtros["municipio"]), width="stretch"
    )

    st.divider()
    tabela = construir_tabela(base_tabela)
    _renderizar_tabela(tabela)
    botoes_exportar_tabela(tabela, "regionalizacao")


def _renderizar_filtros(base: pd.DataFrame) -> dict:
    listas = construir_listas_filtro(base)

    col1, col2, col3 = st.columns(3)
    with col1:
        uo = st.multiselect("Unidade Orçamentária", listas["uo"], key=_CHAVES_FILTRO["uo"])
    with col2:
        acao = st.multiselect("Ação Orçamentária", listas["acao"], key=_CHAVES_FILTRO["acao"])
    with col3:
        regiao = st.multiselect(
            "Região Geográfica Intermediária", listas["regiao"], key=_CHAVES_FILTRO["regiao"]
        )

    col4, col5, col6 = st.columns(3)
    with col4:
        municipio = st.multiselect("Município", listas["municipio"], key=_CHAVES_FILTRO["municipio"])
    with col5:
        produto = st.multiselect("Produto", listas["produto"], key=_CHAVES_FILTRO["produto"])
    with col6:
        st.write("")
        st.button("Limpar filtros", on_click=_limpar_filtros)

    return {"uo": uo, "acao": acao, "regiao": regiao, "municipio": municipio, "produto": produto}


def _aplicar_filtros(base: pd.DataFrame, filtros: dict, ignorar_municipio: bool) -> pd.DataFrame:
    filtrado = base
    if filtros["uo"]:
        filtrado = filtrado[filtrado["uo_label"].isin(filtros["uo"])]
    if filtros["acao"]:
        filtrado = filtrado[filtrado["acao_label"].isin(filtros["acao"])]
    if filtros["regiao"]:
        filtrado = filtrado[filtrado["regiao"].isin(filtros["regiao"])]
    if filtros["produto"]:
        filtrado = filtrado[filtrado["produto"].isin(filtros["produto"])]
    if not ignorar_municipio and filtros["municipio"]:
        filtrado = filtrado[filtrado["municipio"].isin(filtros["municipio"])]
    return filtrado


def _limpar_filtros() -> None:
    for chave in _CHAVES_FILTRO.values():
        st.session_state[chave] = []


_LIMITE_TABELA = 2000


def _renderizar_tabela(tabela: pd.DataFrame) -> None:
    colunas = list(tabela.columns)
    cabecalho = "".join(f"<th>{html.escape(coluna)}</th>" for coluna in colunas)

    total_linhas = len(tabela)
    tabela_exibida = tabela.head(_LIMITE_TABELA)

    linhas_html = []
    for _, linha in tabela_exibida.iterrows():
        celulas = "".join(f"<td>{html.escape(str(linha[coluna]))}</td>" for coluna in colunas)
        linhas_html.append(f"<tr>{celulas}</tr>")

    if total_linhas > _LIMITE_TABELA:
        aviso = (
            f"Mostrando as {_LIMITE_TABELA} linhas de maior valor, de um total de "
            f"{total_linhas}. Use os filtros para refinar."
        )
        linhas_html.append(
            f'<tr><td colspan="{len(colunas)}" style="text-align:center;color:#616e7c;">'
            f"{html.escape(aviso)}</td></tr>"
        )

    st.markdown(
        f"""
        <div class="tabela-regionalizacao-wrapper">
          <table class="tabela-regionalizacao">
            <thead><tr>{cabecalho}</tr></thead>
            <tbody>{''.join(linhas_html)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
