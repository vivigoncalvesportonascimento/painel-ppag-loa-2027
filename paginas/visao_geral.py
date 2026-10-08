"""Página 2: dados gerais do orçamento 2027."""

import pandas as pd
import plotly.express as px
import streamlit as st

from etl.limpeza_inicial import carregar_acoes, carregar_programas
from etl.orcamento import carregar_qdd_fiscal, carregar_qdd_investimento
from utils import formatar_bilhoes

COLUNA_PREVISAO_2027 = "Previsão Orçamentária 2027"

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


def renderizar() -> None:
    st.title("Visão Geral")
    st.caption("Dados gerais do orçamento 2027")
    st.markdown(_CSS_CARDS_CENTRALIZADOS, unsafe_allow_html=True)

    _renderizar_cards()
    st.divider()
    _renderizar_graficos()


def _renderizar_cards() -> None:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_fiscal = carregar_qdd_fiscal()["VALOR FINAL (R$)"].sum()
        st.metric("Previsão 2027 - Orçamento Fiscal", formatar_bilhoes(total_fiscal))

    with col2:
        total_investimento = carregar_qdd_investimento()["VALOR (R$)"].sum()
        st.metric(
            "Previsão 2027 - Orçamento de Investimentos",
            formatar_bilhoes(total_investimento),
        )

    with col3:
        qtd_programas = carregar_programas()["Código do Programa"].nunique()
        st.metric("Quantidade de Programas", qtd_programas)

    with col4:
        qtd_acoes = len(carregar_acoes())
        st.metric("Quantidade de Ações", qtd_acoes)

    with col5:
        acoes = carregar_acoes()
        coluna_iag = "Código do Identificador de Ação Governamental (IAG)"
        projetos_estrategicos = acoes[acoes[coluna_iag] == "1"]
        st.metric("Projetos Estratégicos", len(projetos_estrategicos))


def _renderizar_graficos() -> None:
    acoes = carregar_acoes().copy()
    acoes[COLUNA_PREVISAO_2027] = pd.to_numeric(acoes[COLUNA_PREVISAO_2027])

    col1, col2 = st.columns(2)
    with col1:
        fig = _grafico_percentual_por_categoria(
            acoes, "Área Temática", "Previsão 2027 por Área Temática"
        )
        st.plotly_chart(fig, width="stretch")
    with col2:
        fig = _grafico_percentual_por_categoria(
            acoes, "Setor de Governo", "Previsão 2027 por Setor de Governo"
        )
        st.plotly_chart(fig, width="stretch")


def _grafico_percentual_por_categoria(
    df: pd.DataFrame, coluna_categoria: str, titulo: str
) -> "px.Figure":
    categorias = df[coluna_categoria].str.strip()
    agrupado = df.groupby(categorias)[COLUNA_PREVISAO_2027].sum()
    percentual = (agrupado / agrupado.sum() * 100).sort_values(ascending=True)

    percentual_df = percentual.reset_index()
    percentual_df.columns = [coluna_categoria, "percentual"]

    fig = px.bar(
        percentual_df,
        x="percentual",
        y=coluna_categoria,
        orientation="h",
        title=titulo,
        text=percentual_df["percentual"].map(lambda v: f"{v:.1f}%"),
        labels={"percentual": "% do total", coluna_categoria: ""},
    )
    fig.update_traces(textfont_size=16, textposition="outside")
    fig.update_layout(
        showlegend=False,
        yaxis=dict(tickfont=dict(size=14)),
    )
    return fig
