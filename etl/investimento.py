"""Carregamento das bases usadas na página LOA Investimentos."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AUXILIARES_DIR = Path(__file__).resolve().parent.parent / "auxiliares"

ANO_REFERENCIA = 2027


def carregar_auxiliar_uo() -> pd.DataFrame:
    return pd.read_csv(AUXILIARES_DIR / "auxiliar_uo.csv", sep=";", encoding="cp1252")


def carregar_receita_investimento() -> pd.DataFrame:
    df = pd.read_excel(DATA_DIR / "BASE_ORCAM_RECEITA_INVESTIMENTO.xlsx")
    return df[df["ANO"] == ANO_REFERENCIA]
