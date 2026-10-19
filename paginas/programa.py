"""Página 11: Programa."""

import html

import streamlit as st

from dados_programa import (
    construir_base_enriquecida,
    construir_cards,
    construir_listas_filtro,
    construir_tabela_indicadores,
    selecionar_programa,
)
from exportacao import botoes_exportar_tabela

_CSS_PAGINA = """
<style>
.acao-card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
.acao-card .rotulo {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: #616e7c;
    margin-bottom: 0.4rem;
}
.acao-card .valor {
    font-size: 0.92rem;
    color: #1f2933;
    line-height: 1.5;
}
.acao-card--destaque {
    text-align: center;
}
.acao-card--destaque .valor {
    font-size: 1.35rem;
    font-weight: 700;
    color: #0047AB;
}
.acao-card ul.lista-simples {
    margin: 0;
    padding-left: 1.1rem;
    max-height: 160px;
    overflow-y: auto;
    font-size: 0.92rem;
    color: #1f2933;
    line-height: 1.6;
}
.tabela-indicadores-wrapper {
    max-height: 420px;
    overflow-y: auto;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.tabela-indicadores {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.85rem;
    background: #ffffff;
}
.tabela-indicadores th {
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
.tabela-indicadores td {
    padding: 0.45rem 0.75rem;
    border-top: 1px solid #eef1f4;
    white-space: normal;
    overflow-wrap: break-word;
    word-break: break-word;
}
.tabela-indicadores tbody tr:hover {
    background: #fafbfc;
}
</style>
"""

_CHAVE_FILTRO_UO = "programa_filtro_uo"
_CHAVE_FILTRO_PROGRAMA = "programa_filtro_programa"


def renderizar() -> None:
    st.title("Programa")
    st.markdown(_CSS_PAGINA, unsafe_allow_html=True)

    base = construir_base_enriquecida()
    uo_selecionada, programa_selecionado = _renderizar_filtros(base)

    linhas_programa = selecionar_programa(base, uo_selecionada, programa_selecionado)
    cards = construir_cards(linhas_programa)

    _card_texto("Programa", cards["programa"], destaque=True)

    col2, col3 = st.columns([3, 7])
    with col2:
        _card_texto("Unidade Orçamentária", cards["uo"])
    with col3:
        _card_texto("Área Temática", cards["area_tematica"])

    col4, col5 = st.columns([7, 3])
    with col4:
        _card_texto("Objetivo", cards["objetivo"])
    with col5:
        _card_lista("Objetivo de Desenvolvimento Sustentável - ODS", cards["ods"])

    st.divider()
    st.subheader("Indicadores")
    tabela_indicadores = construir_tabela_indicadores(cards["codigo_programa"])
    _renderizar_tabela(tabela_indicadores)
    botoes_exportar_tabela(tabela_indicadores, "indicadores_programa")


def _renderizar_filtros(base) -> tuple[str, str]:
    listas = construir_listas_filtro(base)

    col1, col2, col3 = st.columns([3, 3, 1])
    with col1:
        uo = st.selectbox(
            "Unidade Orçamentária", [""] + listas["uo"], key=_CHAVE_FILTRO_UO, format_func=_rotulo_selecione
        )
    with col2:
        programa = st.selectbox(
            "Programa", [""] + listas["programa"], key=_CHAVE_FILTRO_PROGRAMA, format_func=_rotulo_selecione
        )
    with col3:
        st.write("")
        st.button("Limpar filtros", on_click=_limpar_filtros)

    return uo, programa


def _rotulo_selecione(valor: str) -> str:
    return valor if valor else "Selecione..."


def _limpar_filtros() -> None:
    st.session_state[_CHAVE_FILTRO_UO] = ""
    st.session_state[_CHAVE_FILTRO_PROGRAMA] = ""


def _card_texto(titulo: str, valor: str, destaque: bool = False) -> None:
    classe = "acao-card acao-card--destaque" if destaque else "acao-card"
    st.markdown(
        f"""
        <div class="{classe}">
          <div class="rotulo">{html.escape(titulo)}</div>
          <div class="valor">{html.escape(str(valor))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _card_lista(titulo: str, itens: list[str]) -> None:
    linhas_html = "".join(f"<li>{html.escape(item)}</li>" for item in itens)
    st.markdown(
        f"""
        <div class="acao-card">
          <div class="rotulo">{html.escape(titulo)}</div>
          <ul class="lista-simples">{linhas_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _renderizar_tabela(tabela) -> None:
    colunas = list(tabela.columns)
    cabecalho = "".join(f"<th>{html.escape(coluna)}</th>" for coluna in colunas)

    linhas_html = []
    for _, linha in tabela.iterrows():
        celulas = "".join(f"<td>{html.escape(str(linha[coluna]))}</td>" for coluna in colunas)
        linhas_html.append(f"<tr>{celulas}</tr>")

    if not linhas_html:
        linhas_html.append(
            f'<tr><td colspan="{len(colunas)}" style="text-align:center;color:#616e7c;">'
            "Nenhum indicador para este programa.</td></tr>"
        )

    st.markdown(
        f"""
        <div class="tabela-indicadores-wrapper">
          <table class="tabela-indicadores">
            <thead><tr>{cabecalho}</tr></thead>
            <tbody>{''.join(linhas_html)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
