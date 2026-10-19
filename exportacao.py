"""Botões de exportação de tabelas (CSV/Excel) compartilhados entre as páginas."""

import io

import pandas as pd
import streamlit as st

_CARACTERES_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def _neutralizar_formula(valor):
    """Evita injeção de fórmula (CSV/Excel injection): se o texto começar com
    um caractere que Excel/Sheets interpretam como início de fórmula, prefixa
    com aspas simples para que seja tratado como texto literal.
    """
    if isinstance(valor, str) and valor.startswith(_CARACTERES_FORMULA):
        return f"'{valor}"
    return valor


def _sanitizar(tabela: pd.DataFrame) -> pd.DataFrame:
    return tabela.map(_neutralizar_formula)


@st.cache_data(show_spinner=False, max_entries=50)
def _gerar_csv(tabela: pd.DataFrame) -> bytes:
    return _sanitizar(tabela).to_csv(index=False, sep=";").encode("utf-8-sig")


@st.cache_data(show_spinner=False, max_entries=50)
def _gerar_excel(tabela: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    _sanitizar(tabela).to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()


def botoes_exportar_tabela(tabela: pd.DataFrame, nome_base: str) -> None:
    """Renderiza dois botões de download (CSV e Excel) para a tabela dada.

    `nome_base` também compõe a key dos widgets, então deve ser único por
    página/tabela para não colidir com outras tabelas da mesma execução do
    app (o Streamlit reexecuta todas as abas a cada rerun). A geração dos
    bytes é cacheada (`st.cache_data`) para não reconverter a tabela inteira
    a cada rerun quando os dados filtrados não mudaram.
    """
    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        st.download_button(
            "⬇ CSV",
            data=_gerar_csv(tabela),
            file_name=f"{nome_base}.csv",
            mime="text/csv",
            key=f"exportar_csv_{nome_base}",
        )
    with col2:
        st.download_button(
            "⬇ Excel",
            data=_gerar_excel(tabela),
            file_name=f"{nome_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"exportar_xlsx_{nome_base}",
        )
