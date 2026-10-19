"""Página 12: QDD (Quadro de Detalhamento da Despesa)."""

import html

import pandas as pd
import streamlit as st

from dados_qdd import construir_base_enriquecida, construir_listas_filtro, construir_tabela
from exportacao import botoes_exportar_tabela

_CSS_PAGINA = """
<style>
.tabela-qdd-wrapper {
    max-height: 520px;
    overflow-y: auto;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.tabela-qdd {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.82rem;
    background: #ffffff;
}
.tabela-qdd th {
    position: sticky;
    top: 0;
    z-index: 1;
    text-align: left;
    background: #eef1f4;
    padding: 0.5rem 0.65rem;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: #616e7c;
    box-shadow: inset 0 -1px 0 #cbd2d9;
    overflow: auto;
    resize: horizontal;
    min-width: 70px;
}
.tabela-qdd td {
    padding: 0.4rem 0.65rem;
    border-top: 1px solid #eef1f4;
    white-space: normal;
    overflow-wrap: break-word;
    word-break: break-word;
}
.tabela-qdd td:last-child {
    text-align: right;
    font-weight: 600;
}
.tabela-qdd tbody tr:hover {
    background: #fafbfc;
}
</style>
"""

_FILTROS = [
    ("uo", "Unidade Orçamentária"),
    ("programa", "Programa"),
    ("acao", "Ação Orçamentária"),
    ("grupo", "Grupo de Despesa"),
    ("iag", "IAG"),
    ("fonte", "Fonte de Recursos"),
    ("ipu", "IPU"),
    ("elemento", "Elemento de Despesa"),
]
_CHAVE_PREFIXO = "qdd_filtro_"
_COLUNA_BASE = {
    "uo": "uo_label",
    "programa": "programa_label",
    "acao": "acao_label",
    "grupo": "grupo_label",
    "iag": "iag_label",
    "fonte": "fonte_label",
    "ipu": "ipu_label",
    "elemento": "elemento_label",
}


def renderizar() -> None:
    st.title("QDD")
    st.caption("Quadro de Detalhamento da Despesa")
    st.markdown(_CSS_PAGINA, unsafe_allow_html=True)

    base = construir_base_enriquecida()
    filtros = _renderizar_filtros(base)

    base_filtrada = base
    for chave, coluna in _COLUNA_BASE.items():
        if filtros[chave]:
            base_filtrada = base_filtrada[base_filtrada[coluna] == filtros[chave]]

    tabela = construir_tabela(base_filtrada)
    _renderizar_tabela(tabela)
    botoes_exportar_tabela(tabela, "qdd")


def _renderizar_filtros(base: pd.DataFrame) -> dict:
    listas = construir_listas_filtro(base)
    valores = {}

    linha1 = st.columns(4)
    for coluna_st, (chave, rotulo) in zip(linha1, _FILTROS[:4]):
        with coluna_st:
            valores[chave] = st.selectbox(
                rotulo,
                [""] + listas[chave],
                key=f"{_CHAVE_PREFIXO}{chave}",
                format_func=_rotulo_selecione,
            )

    linha2 = st.columns([2, 2, 2, 2, 1])
    for coluna_st, (chave, rotulo) in zip(linha2[:4], _FILTROS[4:]):
        with coluna_st:
            valores[chave] = st.selectbox(
                rotulo,
                [""] + listas[chave],
                key=f"{_CHAVE_PREFIXO}{chave}",
                format_func=_rotulo_selecione,
            )
    with linha2[4]:
        st.write("")
        st.button("Limpar filtros", on_click=_limpar_filtros)

    return valores


def _rotulo_selecione(valor: str) -> str:
    return valor if valor else "Todas"


def _limpar_filtros() -> None:
    for chave, _ in _FILTROS:
        st.session_state[f"{_CHAVE_PREFIXO}{chave}"] = ""


def _renderizar_tabela(tabela: pd.DataFrame) -> None:
    colunas = list(tabela.columns)
    cabecalho = "".join(f"<th>{html.escape(coluna)}</th>" for coluna in colunas)

    linhas_html = []
    for _, linha in tabela.iterrows():
        celulas = "".join(f"<td>{html.escape(str(linha[coluna]))}</td>" for coluna in colunas)
        linhas_html.append(f"<tr>{celulas}</tr>")

    if not linhas_html:
        linhas_html.append(
            f'<tr><td colspan="{len(colunas)}" style="text-align:center;color:#616e7c;">'
            "Nenhum dado para os filtros selecionados.</td></tr>"
        )

    st.markdown(
        f"""
        <div class="tabela-qdd-wrapper">
          <table class="tabela-qdd">
            <thead><tr>{cabecalho}</tr></thead>
            <tbody>{''.join(linhas_html)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
