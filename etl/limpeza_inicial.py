"""Primeiro tratamento das bases de planejamento: remove linhas logicamente excluídas.

Premissa documentada em docs/premissas.md.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _ler_base(nome_arquivo: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / nome_arquivo, sep="|", encoding="utf-8", dtype=str)


def carregar_programas() -> pd.DataFrame:
    df = _ler_base("programas_planejamento.txt")
    return df[df["Exclusão Lógica do Programa"] == "Não"]


def carregar_acoes() -> pd.DataFrame:
    df = _ler_base("acoes_planejamento.txt")
    excluido = (df["Exclusão Lógica do Programa"] == "Não") & (
        df["Exclusão Lógica da Ação"] == "Não"
    )
    return df[excluido]


def carregar_localizadores() -> pd.DataFrame:
    df = _ler_base("localizadores_todos_planejamento.txt")
    return df[df["Exclusão Lógica do Programa"] == "False"]


def carregar_indicadores() -> pd.DataFrame:
    df = _ler_base("indicadores_planejamento.txt")
    excluido = (df["Exclusão Lógica do Indicador"] == "False") & (
        df["Exclusão Lógica do Programa"] == "False"
    )
    return df[excluido]
