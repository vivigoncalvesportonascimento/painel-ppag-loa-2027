"""Cálculos da página "QDD" (Quadro de Detalhamento da Despesa),
compartilhados entre o app Streamlit e o gerador do site estático.

BASE_QDD_FISCAL.xlsx é a tabela fato; as 6 bases auxiliares (UO, Grupo
de Despesa, IAG, Fonte de Recursos, IPU, Elemento de Despesa) são
dimensões que se ligam a ela por código. Todos os 6 cruzamentos batem
sem nenhuma lacuna (conferido antes de implementar).
"""

import pandas as pd

from etl.despesa import carregar_auxiliar_grupo_despesa
from etl.investimento import carregar_auxiliar_uo
from etl.orcamento import carregar_qdd_fiscal
from etl.qdd import (
    carregar_auxiliar_elemento_despesa,
    carregar_auxiliar_iag,
    carregar_auxiliar_ipu,
)
from etl.receita import carregar_auxiliar_fonte
from utils import formatar_moeda

COLUNA_VALOR = "VALOR FINAL (R$)"

_COLUNAS_DIMENSAO = [
    "uo_label",
    "programa_label",
    "acao_label",
    "grupo_label",
    "iag_label",
    "fonte_label",
    "ipu_label",
    "elemento_label",
]


def construir_base_enriquecida() -> pd.DataFrame:
    df = carregar_qdd_fiscal().copy()

    df = df.merge(carregar_auxiliar_uo(), left_on="COD_UO", right_on="uo_cod")
    df = df.merge(carregar_auxiliar_grupo_despesa(), left_on="GRUPO_DESPESA", right_on="grupo_despesa_cod")
    df = df.merge(carregar_auxiliar_iag(), left_on="IAG", right_on="iag_cod")
    df = df.merge(carregar_auxiliar_fonte(), left_on="FONTE", right_on="fonte_cod")
    df = df.merge(carregar_auxiliar_ipu(), left_on="IPU", right_on="ipu_cod")
    df = df.merge(
        carregar_auxiliar_elemento_despesa(), left_on="ELEMENTO_DESPESA", right_on="elemento_despesa_cod"
    )

    return pd.DataFrame(
        {
            "uo_label": df["COD_UO"].astype(str) + " - " + df["uo_sigla"],
            "programa_label": df["PROGRAMA"].astype(str) + " - " + df["NOME_PROGRAMA"],
            "acao_label": df["AÇÃO"].astype(str) + " - " + df["NOME_ACAO"],
            "grupo_label": df["GRUPO_DESPESA"].astype(str) + " - " + df["grupo_despesa_descricao"],
            "iag_label": df["IAG"].astype(str) + " - " + df["iag_descricao"],
            "fonte_label": df["FONTE"].astype(str) + " - " + df["fonte_descricao"],
            "ipu_label": df["IPU"].astype(str) + " - " + df["ipu_descricao"],
            "elemento_label": df["ELEMENTO_DESPESA"].astype(str) + " - " + df["elemento_despesa_descricao"],
            COLUNA_VALOR: df[COLUNA_VALOR],
        }
    )


def construir_listas_filtro(base: pd.DataFrame) -> dict:
    return {
        "uo": sorted(base["uo_label"].unique()),
        "programa": sorted(base["programa_label"].unique()),
        "acao": sorted(base["acao_label"].unique()),
        "grupo": sorted(base["grupo_label"].unique()),
        "iag": sorted(base["iag_label"].unique()),
        "fonte": sorted(base["fonte_label"].unique()),
        "ipu": sorted(base["ipu_label"].unique()),
        "elemento": sorted(base["elemento_label"].unique()),
    }


def construir_tabela(base: pd.DataFrame) -> pd.DataFrame:
    agrupado = base.groupby(_COLUNAS_DIMENSAO)[COLUNA_VALOR].sum().reset_index()
    agrupado = agrupado.sort_values(COLUNA_VALOR, ascending=False)

    tabela = pd.DataFrame(
        {
            "Unidade Orçamentária": agrupado["uo_label"],
            "Programa": agrupado["programa_label"],
            "Ação Orçamentária": agrupado["acao_label"],
            "Grupo de Despesa": agrupado["grupo_label"],
            "IAG": agrupado["iag_label"],
            "Fonte de Recursos": agrupado["fonte_label"],
            "IPU": agrupado["ipu_label"],
            "Elemento de Despesa": agrupado["elemento_label"],
            "LOA 2027 (R$)": agrupado[COLUNA_VALOR].map(formatar_moeda),
        }
    )
    return tabela.reset_index(drop=True)
