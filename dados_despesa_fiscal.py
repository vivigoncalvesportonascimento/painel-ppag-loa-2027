"""Cálculos da página "Despesa Fiscal", usados pelo gerador do site
estático (GitHub Pages).

Premissa (ver docs/premissas.md): o cruzamento com auxiliar_poder.csv é
feito por COD_UO (não COD_ORGAO) — é a chave que realmente corresponde
a uo_cod sem lacunas.
"""

import plotly.express as px

from etl.despesa import (
    carregar_auxiliar_funcao,
    carregar_auxiliar_grupo_despesa,
    carregar_auxiliar_poder,
)
from etl.orcamento import carregar_qdd_fiscal
from graficos import grafico_absoluto_vertical, grafico_percentual_horizontal

COLUNA_VALOR = "VALOR FINAL (R$)"


def calcular_card_despesa_total() -> float:
    return carregar_qdd_fiscal()[COLUNA_VALOR].sum()


def construir_grafico_despesa_por_poder() -> "px.Figure":
    despesa = carregar_qdd_fiscal()
    poder = carregar_auxiliar_poder()
    combinado = despesa.merge(poder, left_on="COD_UO", right_on="uo_cod")
    return grafico_absoluto_vertical(
        combinado, "uo_poder", COLUNA_VALOR, "Despesa por Poder e Reserva de Contingência"
    )


def construir_grafico_despesa_por_grupo() -> "px.Figure":
    despesa = carregar_qdd_fiscal()
    grupo = carregar_auxiliar_grupo_despesa()
    combinado = despesa.merge(grupo, left_on="GRUPO_DESPESA", right_on="grupo_despesa_cod")
    return grafico_percentual_horizontal(
        combinado, "grupo_despesa_descricao", COLUNA_VALOR, "Despesa por Grupo"
    )


def construir_grafico_despesa_por_funcao() -> "px.Figure":
    despesa = carregar_qdd_fiscal()
    funcao = carregar_auxiliar_funcao()
    combinado = despesa.merge(funcao, left_on="FUNCAO", right_on="funcao_cod")
    return grafico_percentual_horizontal(
        combinado, "funcao_descricao", COLUNA_VALOR, "Despesa por Função"
    )
