"""Carregamento das tabelas auxiliares exclusivas da página QDD.

auxiliar_uo (etl.investimento), auxiliar_grupo_despesa (etl.despesa) e
auxiliar_fonte (etl.receita) já têm loader em outro módulo e são
reaproveitados aqui.
"""

from pathlib import Path

import pandas as pd

AUXILIARES_DIR = Path(__file__).resolve().parent.parent / "auxiliares"

_ENCODING = "cp1252"


def carregar_auxiliar_iag() -> pd.DataFrame:
    return pd.read_csv(AUXILIARES_DIR / "auxiliar_iag.csv", sep=";", encoding=_ENCODING)


def carregar_auxiliar_ipu() -> pd.DataFrame:
    return pd.read_csv(AUXILIARES_DIR / "auxiliar_ipu.csv", sep=";", encoding=_ENCODING)


def carregar_auxiliar_elemento_despesa() -> pd.DataFrame:
    return pd.read_csv(
        AUXILIARES_DIR / "auxiliar_elemento_despesa.csv", sep=";", encoding=_ENCODING
    )
