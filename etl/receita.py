"""Carregamento das bases de receita fiscal e suas tabelas auxiliares."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AUXILIARES_DIR = Path(__file__).resolve().parent.parent / "auxiliares"

ANO_REFERENCIA = 2027

_ENCODING_AUXILIARES = "cp1252"


def carregar_receita_fiscal() -> pd.DataFrame:
    df = pd.read_excel(DATA_DIR / "BASE_ORCAM_RECEITA_FISCAL.xlsx")
    return df[df["ANO"] == ANO_REFERENCIA]


def carregar_auxiliar_receita_categoria() -> pd.DataFrame:
    return pd.read_csv(
        AUXILIARES_DIR / "auxiliar_receita_categoria.csv",
        sep=";",
        encoding=_ENCODING_AUXILIARES,
    )


def carregar_auxiliar_fonte() -> pd.DataFrame:
    return pd.read_csv(
        AUXILIARES_DIR / "auxiliar_fonte.csv",
        sep=";",
        encoding=_ENCODING_AUXILIARES,
    )
