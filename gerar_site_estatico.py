"""Gera site_estatico/dados.json a partir dos mesmos cálculos do app Streamlit.

Rodar sempre que os dados ou a lógica de visao_geral mudarem, antes de
publicar a branch gh-pages.
"""

import json
from pathlib import Path

from dados_receita_fiscal import (
    calcular_card_receita_total,
    construir_grafico_receita_por_categoria,
    construir_tabela_uo_fonte,
)
from dados_visao_geral import (
    calcular_cards,
    construir_grafico_area_tematica,
    construir_grafico_setor_governo,
)
from utils import formatar_bilhoes

SAIDA = Path(__file__).resolve().parent / "site_estatico" / "dados.json"


def gerar() -> None:
    cards = calcular_cards()

    dados = {
        "cards": [
            {
                "titulo": "Previsão 2027 - Orçamento Fiscal",
                "valor": formatar_bilhoes(cards["total_fiscal"]),
            },
            {
                "titulo": "Previsão 2027 - Orçamento de Investimentos",
                "valor": formatar_bilhoes(cards["total_investimento"]),
            },
            {
                "titulo": "Quantidade de Programas",
                "valor": f"{cards['qtd_programas']:,}".replace(",", "."),
            },
            {
                "titulo": "Quantidade de Ações",
                "valor": f"{cards['qtd_acoes']:,}".replace(",", "."),
            },
            {
                "titulo": "Projetos Estratégicos",
                "valor": f"{cards['qtd_projetos_estrategicos']:,}".replace(",", "."),
            },
        ],
        "grafico_area_tematica": json.loads(construir_grafico_area_tematica().to_json()),
        "grafico_setor_governo": json.loads(construir_grafico_setor_governo().to_json()),
        "receita_fiscal": {
            "card_receita_total": formatar_bilhoes(calcular_card_receita_total()),
            "grafico_categoria": json.loads(
                construir_grafico_receita_por_categoria().to_json()
            ),
            "tabela_uo_fonte": construir_tabela_uo_fonte().to_dict(orient="records"),
        },
    }

    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gerado: {SAIDA}")


if __name__ == "__main__":
    gerar()
