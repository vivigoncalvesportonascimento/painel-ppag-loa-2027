"""Gera site_estatico/dados.json a partir dos mesmos cálculos do app Streamlit.

Rodar sempre que os dados ou a lógica de visao_geral mudarem, antes de
publicar a branch gh-pages.
"""

import json
from pathlib import Path

from dados_despesa_fiscal import (
    calcular_card_despesa_total,
    construir_grafico_despesa_por_funcao,
    construir_grafico_despesa_por_grupo,
    construir_grafico_despesa_por_poder,
)
from dados_despesa_orgao import COLUNA_VALOR as COLUNA_VALOR_DESPESA
from dados_despesa_orgao import construir_base_enriquecida as construir_base_despesa_orgao
from dados_loa_investimentos import (
    construir_base_despesa as construir_base_investimentos_despesa,
)
from dados_loa_investimentos import (
    construir_base_receita as construir_base_investimentos_receita,
)
from dados_loa_investimentos import construir_lista_uo as construir_lista_uo_investimentos
from dados_receita_fiscal import COLUNA_VALOR, construir_base_enriquecida
from dados_regionalizacao import construir_base_enriquecida as construir_base_regionalizacao
from dados_visao_geral import (
    calcular_cards,
    construir_grafico_area_tematica,
    construir_grafico_setor_governo,
)
from utils import formatar_bilhoes

PASTA_SAIDA = Path(__file__).resolve().parent / "site_estatico"
SAIDA = PASTA_SAIDA / "dados.json"
SAIDA_REGIONALIZACAO = PASTA_SAIDA / "dados_regionalizacao.json"


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
            "linhas": construir_base_enriquecida().rename(
                columns={COLUNA_VALOR: "valor"}
            ).to_dict(orient="records"),
        },
        "despesa_fiscal": {
            "card_despesa_total": formatar_bilhoes(calcular_card_despesa_total()),
            "grafico_poder": json.loads(construir_grafico_despesa_por_poder().to_json()),
            "grafico_grupo": json.loads(construir_grafico_despesa_por_grupo().to_json()),
            "grafico_funcao": json.loads(construir_grafico_despesa_por_funcao().to_json()),
        },
        "despesa_orgao": {
            "linhas": construir_base_despesa_orgao()
            .rename(columns={COLUNA_VALOR_DESPESA: "valor"})
            .to_dict(orient="records"),
        },
        "loa_investimentos": {
            "uo_opcoes": construir_lista_uo_investimentos(),
            "linhas_receita": construir_base_investimentos_receita().to_dict(orient="records"),
            "linhas_despesa": construir_base_investimentos_despesa().to_dict(orient="records"),
        },
    }

    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gerado: {SAIDA}")

    # Arquivo separado (carregado só quando a aba Regionalização é aberta):
    # a base tem ~40 mil linhas e deixaria o carregamento inicial do site
    # mais pesado se fosse embutida em dados.json.
    regionalizacao = construir_base_regionalizacao().rename(
        columns={
            "Previsão Física 2027": "fisica",
            "Previsão Orçamentária 2027": "valor",
        }
    )
    SAIDA_REGIONALIZACAO.write_text(
        json.dumps({"linhas": regionalizacao.to_dict(orient="records")}, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Gerado: {SAIDA_REGIONALIZACAO}")


if __name__ == "__main__":
    gerar()
