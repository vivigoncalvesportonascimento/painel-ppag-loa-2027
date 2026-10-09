"""Cálculos da página "Visão Geral", compartilhados entre o app Streamlit
e o gerador do site estático (GitHub Pages).
"""

import pandas as pd
import plotly.express as px

from etl.limpeza_inicial import carregar_acoes, carregar_programas
from etl.orcamento import carregar_qdd_fiscal, carregar_qdd_investimento
from graficos import grafico_percentual_horizontal

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
    return grafico_percentual_horizontal(
        df, "Área Temática", COLUNA_PREVISAO_2027, "Previsão 2027 por Área Temática"
    )


def construir_grafico_setor_governo() -> "px.Figure":
    return grafico_percentual_horizontal(
        _carregar_acoes_numericas(),
        "Setor de Governo",
        COLUNA_PREVISAO_2027,
        "Previsão 2027 por Setor de Governo",
    )


def _carregar_acoes_numericas() -> pd.DataFrame:
    acoes = carregar_acoes().copy()
    acoes[COLUNA_PREVISAO_2027] = pd.to_numeric(acoes[COLUNA_PREVISAO_2027])
    return acoes
