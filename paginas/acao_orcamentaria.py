"""Página 10: Ação Orçamentária."""

import html

import streamlit as st

from dados_acao_orcamentaria import (
    construir_base_enriquecida,
    construir_cards,
    construir_grafico_previsao_fisica,
    construir_grafico_previsao_orcamentaria,
    construir_listas_filtro,
    selecionar_acao,
)

_CSS_PAGINA = """
<style>
.acao-card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    height: calc(100% - 1rem);
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
</style>
"""

_CHAVE_FILTRO_UO = "acao_orcamentaria_filtro_uo"
_CHAVE_FILTRO_ACAO = "acao_orcamentaria_filtro_acao"


def renderizar() -> None:
    st.title("Ação Orçamentária")
    st.markdown(_CSS_PAGINA, unsafe_allow_html=True)

    base = construir_base_enriquecida()
    uo_selecionada, acao_selecionada = _renderizar_filtros(base)

    linha = selecionar_acao(base, uo_selecionada, acao_selecionada)
    cards = construir_cards(linha)

    _card_texto("Ação Orçamentária", cards["acao"], destaque=True)

    col2, col3 = st.columns([3, 7])
    with col2:
        _card_texto("Unidade Orçamentária", cards["uo"])
    with col3:
        _card_texto("Programa", cards["programa"])

    col4, col5 = st.columns([7, 3])
    with col4:
        _card_texto("Finalidade da Ação", cards["finalidade"])
    with col5:
        _card_texto("Público-Alvo", cards["publico_alvo"])

    col6, col7, col8 = st.columns(3)
    with col6:
        _card_texto("Identificador de Ação Governamental (IAG)", cards["iag"])
    with col7:
        _card_texto("Produto", cards["produto"])
    with col8:
        _card_texto("Unidade de Medida (Produto)", cards["unidade_medida"])

    st.divider()
    col_grafico1, col_grafico2 = st.columns(2)
    with col_grafico1:
        st.plotly_chart(construir_grafico_previsao_fisica(linha), width="stretch")
    with col_grafico2:
        st.plotly_chart(construir_grafico_previsao_orcamentaria(linha), width="stretch")


def _renderizar_filtros(base) -> tuple[str, str]:
    listas = construir_listas_filtro(base)

    col1, col2, col3 = st.columns([3, 3, 1])
    with col1:
        uo = st.selectbox(
            "Unidade Orçamentária", [""] + listas["uo"], key=_CHAVE_FILTRO_UO, format_func=_rotulo_todas
        )
    with col2:
        acao = st.selectbox(
            "Ação Orçamentária", [""] + listas["acao"], key=_CHAVE_FILTRO_ACAO, format_func=_rotulo_todas
        )
    with col3:
        st.write("")
        st.button("Limpar filtros", on_click=_limpar_filtros)

    return uo, acao


def _rotulo_todas(valor: str) -> str:
    return valor if valor else "Selecione..."


def _limpar_filtros() -> None:
    st.session_state[_CHAVE_FILTRO_UO] = ""
    st.session_state[_CHAVE_FILTRO_ACAO] = ""


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
