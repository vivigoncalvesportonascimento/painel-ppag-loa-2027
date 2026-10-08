"""Carregamento das bases de orçamento (QDD fiscal e investimento)."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ANO_REFERENCIA = 2027


def carregar_qdd_fiscal() -> pd.DataFrame:
    df = pd.read_excel(DATA_DIR / "BASE_QDD_FISCAL.xlsx")
    return df[df["ANO"] == ANO_REFERENCIA]


def carregar_qdd_investimento() -> pd.DataFrame:
    df = pd.read_excel(DATA_DIR / "BASE_QDD_INVESTIMENTO.xlsx")
    return df[df["ANO"] == ANO_REFERENCIA]
