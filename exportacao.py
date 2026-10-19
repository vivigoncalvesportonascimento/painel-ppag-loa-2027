"""Botões de exportação de tabelas (CSV/Excel) compartilhados entre as páginas."""

import io

import pandas as pd
import streamlit as st


def botoes_exportar_tabela(tabela: pd.DataFrame, nome_base: str) -> None:
    """Renderiza dois botões de download (CSV e Excel) para a tabela dada.

    `nome_base` também compõe a key dos widgets, então deve ser único por
    página/tabela para não colidir com outras tabelas da mesma execução do
    app (o Streamlit reexecuta todas as abas a cada rerun).
    """
    csv_bytes = tabela.to_csv(index=False, sep=";").encode("utf-8-sig")

    buffer_excel = io.BytesIO()
    tabela.to_excel(buffer_excel, index=False, engine="openpyxl")

    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        st.download_button(
            "⬇ CSV",
            data=csv_bytes,
            file_name=f"{nome_base}.csv",
            mime="text/csv",
            key=f"exportar_csv_{nome_base}",
        )
    with col2:
        st.download_button(
            "⬇ Excel",
            data=buffer_excel.getvalue(),
            file_name=f"{nome_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"exportar_xlsx_{nome_base}",
        )
