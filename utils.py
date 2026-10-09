"""Utilidades de formatação compartilhadas entre as páginas do painel."""

import math


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def formatar_bilhoes(valor: float) -> str:
    bilhoes = valor / 1_000_000_000
    truncado = math.floor(bilhoes * 10) / 10
    texto = f"{truncado:.1f}".replace(".", ",")
    return f"R$ {texto} bi"


def formatar_bi_arredondado(valor: float) -> str:
    return f"{round(valor / 1_000_000_000)} bi"
