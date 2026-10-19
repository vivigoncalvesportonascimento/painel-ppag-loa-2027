"""Cálculos da página "Ação Orçamentária", usados pelo gerador do site
estático (GitHub Pages).

Página de detalhe: os dois filtros (UO, Ação) selecionam uma única linha
de `acoes_planejamento.txt`, cujos campos de texto alimentam os cards e
cujas colunas de Previsão Física/Orçamentária 2027-2030 são "pivotadas"
(uma coluna por ano) para os dois gráficos.
"""

import pandas as pd
import plotly.graph_objects as go

from etl.limpeza_inicial import carregar_acoes
from utils import formatar_moeda

ANOS = [2027, 2028, 2029, 2030]

_COR_BARRA = "#0047AB"
_FONTE = "system-ui, -apple-system, Segoe UI, Arial, sans-serif"


def construir_base_enriquecida() -> pd.DataFrame:
    df = carregar_acoes().copy()
    df["uo_label"] = (
        df["Código da Unidade Orçamentária Responsável pela Ação"]
        + " - "
        + df["Unidade Orçamentária Responsável pela Ação"]
    )
    df["acao_label"] = df["Código da Ação"] + " - " + df["Título da Ação"]
    df["programa_label"] = df["Código do Programa"] + " - " + df["Nome do Programa"]
    return df


def construir_listas_filtro(base: pd.DataFrame) -> dict:
    return {
        "uo": sorted(base["uo_label"].unique()),
        "acao": sorted(base["acao_label"].unique()),
    }


def selecionar_acao(base: pd.DataFrame, uo_label: str, acao_label: str) -> pd.Series:
    filtrado = base
    if uo_label:
        filtrado = filtrado[filtrado["uo_label"] == uo_label]
    if acao_label:
        filtrado = filtrado[filtrado["acao_label"] == acao_label]
    if filtrado.empty:
        filtrado = base
    return filtrado.sort_values(["uo_label", "acao_label"]).iloc[0]


def construir_cards(linha: pd.Series) -> dict:
    return {
        "acao": linha["acao_label"],
        "uo": linha["uo_label"],
        "programa": linha["programa_label"],
        "finalidade": linha["Finalidade da Ação"],
        "publico_alvo": linha["Público-Alvo"],
        "iag": linha["Identificador de Ação Governamental (IAG)"],
        "produto": linha["Produto"],
        "unidade_medida": linha["Unidade de Medida do Produto"],
    }


def construir_grafico_previsao_fisica(linha: pd.Series) -> "go.Figure":
    return _construir_grafico_ano(
        linha,
        "Previsão Física",
        "Previsão Física",
        lambda v: f"{v:,.0f}".replace(",", "."),
    )


def construir_grafico_previsao_orcamentaria(linha: pd.Series) -> "go.Figure":
    return _construir_grafico_ano(linha, "Previsão Orçamentária", "Previsão Orçamentária", formatar_moeda)


def _construir_grafico_ano(linha: pd.Series, prefixo_coluna: str, titulo: str, formatar) -> "go.Figure":
    valores = [float(linha[f"{prefixo_coluna} {ano}"]) for ano in ANOS]
    textos = [formatar(v) for v in valores]
    valor_max = max(valores) if valores else 0

    fig = go.Figure(
        go.Bar(
            x=[str(ano) for ano in ANOS],
            y=valores,
            text=textos,
            textposition="outside",
            marker=dict(color=_COR_BARRA),
            cliponaxis=False,
        )
    )
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b>", font=dict(size=16, color="#1f2933")),
        showlegend=False,
        height=340,
        font=dict(family=_FONTE, color="#1f2933"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=40),
        xaxis=dict(type="category", tickfont=dict(size=12)),
        yaxis=dict(gridcolor="#eef1f4", range=[0, valor_max * 1.2 if valor_max else 1]),
    )
    return fig
