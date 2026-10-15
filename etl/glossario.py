"""Carregamento da base do glossário."""

from pathlib import Path

import pandas as pd

AUXILIARES_DIR = Path(__file__).resolve().parent.parent / "auxiliares"


def carregar_glossario() -> pd.DataFrame:
    return pd.read_csv(AUXILIARES_DIR / "auxiliar_glossario.csv", sep=";", encoding="cp1252")
