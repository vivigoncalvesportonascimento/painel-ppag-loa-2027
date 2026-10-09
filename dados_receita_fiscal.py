"""Cálculos da página "Receita Fiscal", compartilhados entre o app
Streamlit e o gerador do site estático (GitHub Pages).
"""

import pandas as pd
import plotly.express as px

from etl.receita import (
    carregar_auxiliar_fonte,
    carregar_auxiliar_receita_categoria,
    carregar_receita_fiscal,
)
from utils import formatar_moeda

COLUNA_VALOR = "VALOR FINAL (R$)"


def calcular_card_receita_total() -> float:
    return carregar_receita_fiscal()[COLUNA_VALOR].sum()


def construir_grafico_receita_por_categoria() -> "px.Figure":
    receita = carregar_receita_fiscal()
    categorias = carregar_auxiliar_receita_categoria()

    agrupado = receita.groupby("CATEGORIA")[COLUNA_VALOR].sum().reset_index()
    agrupado = agrupado.merge(
        categorias, left_on="CATEGORIA", right_on="categoria_receita_cod"
    )
    agrupado = agrupado.sort_values(COLUNA_VALOR, ascending=True)

    fig = px.bar(
        agrupado,
        x=COLUNA_VALOR,
        y="categoria_receita_desc",
        orientation="h",
        title="<b>Receitas por Categoria Econômica</b>",
        text=agrupado[COLUNA_VALOR].map(_formatar_bi_arredondado),
        labels={COLUNA_VALOR: "Valor (R$)", "categoria_receita_desc": ""},
        color_discrete_sequence=["#0047AB"],
    )
    fig.update_traces(textfont_size=15, textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=280,
        font=dict(family="system-ui, -apple-system, Segoe UI, Arial, sans-serif", color="#1f2933"),
        title=dict(font=dict(size=16, color="#1f2933")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=30, t=40, b=10),
        yaxis=dict(tickfont=dict(size=12), automargin=True),
        xaxis=dict(gridcolor="#eef1f4"),
    )
    return fig


def construir_tabela_uo_fonte() -> pd.DataFrame:
    receita = carregar_receita_fiscal()
    fontes = carregar_auxiliar_fonte()

    agrupado = (
        receita.groupby(["SIGLA_UO", "COD_FONTE"])[COLUNA_VALOR]
        .sum()
        .reset_index()
        .merge(fontes, left_on="COD_FONTE", right_on="fonte_cod")
    )

    tabela = pd.DataFrame(
        {
            "UO": agrupado["SIGLA_UO"],
            "Fonte de Recursos": agrupado["COD_FONTE"].astype(str)
            + " - "
            + agrupado["fonte_descricao"],
            "LOA 2027 (R$)": agrupado[COLUNA_VALOR].map(formatar_moeda),
            "_ordenacao": agrupado[COLUNA_VALOR],
        }
    )
    tabela = tabela.sort_values("_ordenacao", ascending=False).drop(columns="_ordenacao")
    return tabela.reset_index(drop=True)


def _formatar_bi_arredondado(valor: float) -> str:
    return f"{round(valor / 1_000_000_000)} bi"
