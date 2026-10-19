"""Cálculos da página "Despesa por Órgão", usados pelo gerador do site
estático (GitHub Pages).

`construir_base_enriquecida` é a fonte única em nível de linha. O
filtro por Unidade Orçamentária opera sobre essa base ANTES de
qualquer agrupamento (por Grupo, Ação ou Fonte) — é isso que garante
que os valores de Ação/Fonte reflitam a UO selecionada, em vez de
somar sempre a mesma ação/fonte em todas as UOs independentemente do
filtro (ação orçamentária como 2500 e 7004 existem em várias UOs).
"""

import pandas as pd
import plotly.express as px

from etl.despesa import carregar_auxiliar_grupo_despesa
from etl.orcamento import carregar_qdd_fiscal
from etl.receita import carregar_auxiliar_fonte
from graficos import grafico_absoluto_vertical
from utils import formatar_moeda

COLUNA_VALOR = "VALOR FINAL (R$)"
COLUNA_ACAO = "AÇÃO"


def construir_base_enriquecida() -> pd.DataFrame:
    despesa = carregar_qdd_fiscal()
    grupo = carregar_auxiliar_grupo_despesa()
    fonte = carregar_auxiliar_fonte()

    base = despesa.merge(
        grupo, left_on="GRUPO_DESPESA", right_on="grupo_despesa_cod"
    ).merge(fonte, left_on="FONTE", right_on="fonte_cod")

    return pd.DataFrame(
        {
            "uo_label": base["COD_UO"].astype(str) + " - " + base["UO"],
            "grupo_despesa_descricao": base["grupo_despesa_descricao"],
            "acao_label": base[COLUNA_ACAO].astype(str) + " - " + base["NOME_ACAO"],
            "fonte_label": base["FONTE"].astype(str) + " - " + base["fonte_descricao"],
            COLUNA_VALOR: base[COLUNA_VALOR],
        }
    )


def calcular_card_despesa_total(base: pd.DataFrame) -> float:
    return base[COLUNA_VALOR].sum()


def construir_grafico_despesa_por_grupo(base: pd.DataFrame) -> "px.Figure":
    return grafico_absoluto_vertical(
        base, "grupo_despesa_descricao", COLUNA_VALOR, "Despesa por Grupo"
    )


def construir_lista_acao(base: pd.DataFrame) -> list[dict]:
    agrupado = base.groupby("acao_label")[COLUNA_VALOR].sum().reset_index()
    agrupado = agrupado.sort_values(COLUNA_VALOR, ascending=False)
    return [
        {"label": linha["acao_label"], "valor": formatar_moeda(linha[COLUNA_VALOR])}
        for _, linha in agrupado.iterrows()
    ]


def construir_lista_fonte(base: pd.DataFrame) -> list[dict]:
    agrupado = base.groupby("fonte_label")[COLUNA_VALOR].sum().reset_index()
    total = agrupado[COLUNA_VALOR].sum()
    agrupado["percentual"] = agrupado[COLUNA_VALOR] / total * 100
    agrupado = agrupado.sort_values("percentual", ascending=False)
    return [
        {"label": linha["fonte_label"], "valor": f"{linha['percentual']:.1f}%"}
        for _, linha in agrupado.iterrows()
    ]
