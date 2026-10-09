"""Cálculos da página "Despesa Fiscal", compartilhados entre o app
Streamlit e o gerador do site estático (GitHub Pages).

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
from graficos import grafico_percentual_horizontal
from utils import formatar_bi_arredondado

COLUNA_VALOR = "VALOR FINAL (R$)"


def calcular_card_despesa_total() -> float:
    return carregar_qdd_fiscal()[COLUNA_VALOR].sum()


def construir_grafico_despesa_por_poder() -> "px.Figure":
    despesa = carregar_qdd_fiscal()
    poder = carregar_auxiliar_poder()

    combinado = despesa.merge(poder, left_on="COD_UO", right_on="uo_cod")
    agrupado = combinado.groupby("uo_poder")[COLUNA_VALOR].sum().reset_index()
    agrupado = agrupado.sort_values(COLUNA_VALOR, ascending=False)

    fig = px.bar(
        agrupado,
        x="uo_poder",
        y=COLUNA_VALOR,
        title="<b>Despesa por Poder e Reserva de Contingência</b>",
        text=agrupado[COLUNA_VALOR].map(formatar_bi_arredondado),
        labels={COLUNA_VALOR: "Valor (R$)", "uo_poder": ""},
        color_discrete_sequence=["#0047AB"],
    )
    fig.update_traces(textfont_size=13, textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=340,
        font=dict(family="system-ui, -apple-system, Segoe UI, Arial, sans-serif", color="#1f2933"),
        title=dict(font=dict(size=16, color="#1f2933")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=90),
        xaxis=dict(tickfont=dict(size=11), tickangle=-25, automargin=True),
        yaxis=dict(gridcolor="#eef1f4"),
    )
    return fig


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
