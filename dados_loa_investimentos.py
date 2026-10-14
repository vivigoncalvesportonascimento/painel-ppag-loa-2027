"""Cálculos da página "LOA Investimentos", compartilhados entre o app
Streamlit e o gerador do site estático (GitHub Pages).

A tabela auxiliar_uo.csv funciona como dimensão: só as UOs com
tipo_loa == "loa_investimentos" entram no filtro e nas duas bases de
fato (BASE_ORCAM_RECEITA_INVESTIMENTO.xlsx e BASE_QDD_INVESTIMENTO.xlsx),
ligadas por uo_cod == COD_UO em cada uma delas.
"""

import pandas as pd

from etl.investimento import carregar_auxiliar_uo, carregar_receita_investimento
from etl.orcamento import carregar_qdd_investimento
from utils import formatar_moeda

TIPO_LOA_INVESTIMENTOS = "loa_investimentos"
COLUNA_ACAO = "AÇÃO"


def _carregar_auxiliar_uo_investimentos() -> pd.DataFrame:
    aux = carregar_auxiliar_uo()
    return aux[aux["tipo_loa"] == TIPO_LOA_INVESTIMENTOS]


def construir_lista_uo() -> list[str]:
    aux_inv = _carregar_auxiliar_uo_investimentos()
    labels = aux_inv["uo_cod"].astype(str) + " - " + aux_inv["uo_descricao"]
    return sorted(labels.tolist())


def construir_base_receita() -> pd.DataFrame:
    aux_inv = _carregar_auxiliar_uo_investimentos()
    receita = carregar_receita_investimento()
    base = receita.merge(aux_inv, left_on="COD_UO", right_on="uo_cod")
    return pd.DataFrame(
        {
            "uo_label": base["uo_cod"].astype(str) + " - " + base["uo_descricao"],
            "valor": base["VALOR FINAL (R$)"],
        }
    )


def construir_base_despesa() -> pd.DataFrame:
    aux_inv = _carregar_auxiliar_uo_investimentos()
    despesa = carregar_qdd_investimento()
    base = despesa.merge(aux_inv, left_on="COD_UO", right_on="uo_cod")
    return pd.DataFrame(
        {
            "uo_label": base["uo_cod"].astype(str) + " - " + base["uo_descricao"],
            "uo_sigla": base["uo_sigla"],
            "acao_label": base[COLUNA_ACAO].astype(str) + " - " + base["NOME_ACAO"],
            "valor": base["VALOR (R$)"],
        }
    )


def calcular_card_receita_total(base_receita: pd.DataFrame) -> float:
    return base_receita["valor"].sum()


def calcular_card_despesa_total(base_despesa: pd.DataFrame) -> float:
    return base_despesa["valor"].sum()


def construir_tabela(base_despesa: pd.DataFrame) -> pd.DataFrame:
    agrupado = (
        base_despesa.groupby(["uo_sigla", "acao_label"])["valor"].sum().reset_index()
    )
    agrupado = agrupado.sort_values("valor", ascending=False)

    tabela = pd.DataFrame(
        {
            "Unidade Orçamentária": agrupado["uo_sigla"],
            "Ação Orçamentária": agrupado["acao_label"],
            "LOA 2027 (R$)": agrupado["valor"].map(formatar_moeda),
        }
    )
    return tabela.reset_index(drop=True)
