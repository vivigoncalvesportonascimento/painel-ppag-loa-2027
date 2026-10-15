"""Página 9: Glossário."""

import html

import streamlit as st

from dados_glossario import construir_lista_termos

_CSS_PAGINA = """
<style>
.glossario-painel {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    padding: 1.1rem 1.25rem;
    margin-bottom: 1rem;
}
.glossario-painel h4 {
    margin: 0 0 0.5rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: #616e7c;
}
.glossario-painel p {
    margin: 0;
    font-size: 0.95rem;
    color: #1f2933;
    line-height: 1.5;
}
</style>
"""

_CHAVE_TERMO_SELECIONADO = "glossario_termo_selecionado"
_COLUNAS_POR_LINHA = 5


def renderizar() -> None:
    st.title("Glossário")
    st.markdown(_CSS_PAGINA, unsafe_allow_html=True)

    termos = construir_lista_termos()

    if _CHAVE_TERMO_SELECIONADO not in st.session_state:
        st.session_state[_CHAVE_TERMO_SELECIONADO] = termos[0]["termo"]

    _renderizar_nuvem_termos(termos)
    st.divider()
    _renderizar_painel_detalhe(termos)


def _renderizar_nuvem_termos(termos: list[dict]) -> None:
    for inicio in range(0, len(termos), _COLUNAS_POR_LINHA):
        colunas = st.columns(_COLUNAS_POR_LINHA)
        for coluna, item in zip(colunas, termos[inicio : inicio + _COLUNAS_POR_LINHA]):
            with coluna:
                ativo = st.session_state[_CHAVE_TERMO_SELECIONADO] == item["termo"]
                if st.button(
                    item["termo"],
                    key=f"glossario_botao_{item['termo']}",
                    type="primary" if ativo else "secondary",
                    width="stretch",
                ):
                    st.session_state[_CHAVE_TERMO_SELECIONADO] = item["termo"]


def _renderizar_painel_detalhe(termos: list[dict]) -> None:
    termo_selecionado = st.session_state[_CHAVE_TERMO_SELECIONADO]
    item = next(t for t in termos if t["termo"] == termo_selecionado)

    st.markdown(
        f"""
        <div class="glossario-painel">
          <h4>Definição Técnica</h4>
          <p>{html.escape(item['definicao_tecnica'])}</p>
        </div>
        <div class="glossario-painel">
          <h4>Linguagem Simples</h4>
          <p>{html.escape(item['linguagem_simples'])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
