"""Carregamento das tabelas auxiliares usadas na página Despesa Fiscal.

A base de despesa em si (BASE_QDD_FISCAL.xlsx) é reaproveitada de
etl.orcamento.carregar_qdd_fiscal.
"""

from pathlib import Path

import pandas as pd

AUXILIARES_DIR = Path(__file__).resolve().parent.parent / "auxiliares"

_ENCODING_AUXILIARES = "cp1252"


def carregar_auxiliar_poder() -> pd.DataFrame:
    return pd.read_csv(
        AUXILIARES_DIR / "auxiliar_poder.csv", sep=";", encoding=_ENCODING_AUXILIARES
    )


def carregar_auxiliar_grupo_despesa() -> pd.DataFrame:
    return pd.read_csv(
        AUXILIARES_DIR / "auxiliar_grupo_despesa.csv",
        sep=";",
        encoding=_ENCODING_AUXILIARES,
    )


def carregar_auxiliar_funcao() -> pd.DataFrame:
    return pd.read_csv(
        AUXILIARES_DIR / "auxiliar_funcao.csv", sep=";", encoding=_ENCODING_AUXILIARES
    )
