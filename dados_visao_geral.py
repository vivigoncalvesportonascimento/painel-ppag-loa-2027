"""Cálculos da página "Visão Geral", compartilhados entre o app Streamlit
e o gerador do site estático (GitHub Pages).
"""

import pandas as pd
import plotly.express as px

from etl.limpeza_inicial import carregar_acoes, carregar_programas
from etl.orcamento import carregar_qdd_fiscal, carregar_qdd_investimento

COLUNA_PREVISAO_2027 = "Previsão Orçamentária 2027"
COLUNA_IAG = "Código do Identificador de Ação Governamental (IAG)"


def calcular_cards() -> dict:
    total_fiscal = carregar_qdd_fiscal()["VALOR FINAL (R$)"].sum()
    total_investimento = carregar_qdd_investimento()["VALOR (R$)"].sum()
    qtd_programas = carregar_programas()["Código do Programa"].nunique()

    acoes = carregar_acoes()
    qtd_acoes = len(acoes)
    qtd_projetos_estrategicos = len(acoes[acoes[COLUNA_IAG] == "1"])

    return {
        "total_fiscal": total_fiscal,
        "total_investimento": total_investimento,
        "qtd_programas": qtd_programas,
        "qtd_acoes": qtd_acoes,
        "qtd_projetos_estrategicos": qtd_projetos_estrategicos,
    }


def construir_grafico_area_tematica() -> "px.Figure":
    df = _carregar_acoes_numericas()
    df["Área Temática"] = df["Área Temática"].str.upper()
    return _grafico_percentual_por_categoria(
        df, "Área Temática", "Previsão 2027 por Área Temática"
    )


def construir_grafico_setor_governo() -> "px.Figure":
    return _grafico_percentual_por_categoria(
        _carregar_acoes_numericas(), "Setor de Governo", "Previsão 2027 por Setor de Governo"
    )


def _carregar_acoes_numericas() -> pd.DataFrame:
    acoes = carregar_acoes().copy()
    acoes[COLUNA_PREVISAO_2027] = pd.to_numeric(acoes[COLUNA_PREVISAO_2027])
    return acoes


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
        title=f"<b>{titulo}</b>",
        text=percentual_df["percentual"].map(lambda v: f"{v:.1f}%"),
        labels={"percentual": "% do total", coluna_categoria: ""},
        color_discrete_sequence=["#0047AB"],
    )
    fig.update_traces(textfont_size=13, textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=340,
        font=dict(family="system-ui, -apple-system, Segoe UI, Arial, sans-serif", color="#1f2933"),
        title=dict(font=dict(size=15, color="#1f2933")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=30, t=40, b=10),
        yaxis=dict(tickfont=dict(size=11), automargin=True),
        xaxis=dict(gridcolor="#eef1f4"),
    )
    return fig
