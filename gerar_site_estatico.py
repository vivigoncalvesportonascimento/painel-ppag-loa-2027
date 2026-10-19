"""Gera site_estatico/dados.json a partir dos módulos dados_*.py.

Rodar sempre que os dados ou a lógica de algum dados_*.py mudarem, antes
de publicar a branch gh-pages.
"""

import json
from pathlib import Path

from dados_despesa_fiscal import (
    calcular_card_despesa_total,
    construir_grafico_despesa_por_funcao,
    construir_grafico_despesa_por_grupo,
    construir_grafico_despesa_por_poder,
)
from dados_acao_orcamentaria import ANOS, construir_base_enriquecida as construir_base_acao
from dados_despesa_orgao import COLUNA_VALOR as COLUNA_VALOR_DESPESA
from dados_despesa_orgao import construir_base_enriquecida as construir_base_despesa_orgao
from dados_glossario import construir_lista_termos
from dados_loa_investimentos import (
    construir_base_despesa as construir_base_investimentos_despesa,
)
from dados_loa_investimentos import (
    construir_base_receita as construir_base_investimentos_receita,
)
from dados_loa_investimentos import construir_lista_uo as construir_lista_uo_investimentos
from dados_programa import construir_base_enriquecida as construir_base_programa
from dados_programa import construir_tabela_indicadores
from dados_qdd import COLUNA_VALOR as COLUNA_VALOR_QDD
from dados_qdd import construir_base_enriquecida as construir_base_qdd
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
SAIDA_QDD = PASTA_SAIDA / "dados_qdd.json"


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
        "glossario": construir_lista_termos(),
        "acao_orcamentaria": {
            "linhas": _exportar_acao_orcamentaria(),
        },
        "programa": _exportar_programa(),
    }

    texto_dados = json.dumps(dados, ensure_ascii=False, indent=2)
    _validar_json_estrito(texto_dados, SAIDA.name)
    SAIDA.write_text(texto_dados, encoding="utf-8")
    print(f"Gerado: {SAIDA}")

    # Arquivo separado (carregado só quando a aba Regionalização é aberta):
    # a base tem ~40 mil linhas e deixaria o carregamento inicial do site
    # mais pesado se fosse embutida em dados.json. Os textos (UO, Ação,
    # Região, Produto, Unidade) se repetem muito entre as 40 mil linhas, por
    # isso são codificados por dicionário (cada valor distinto guardado uma
    # única vez, e as linhas referenciam só o índice) — isso sozinho reduz o
    # arquivo de ~14 MB para ~2 MB.
    regionalizacao = construir_base_regionalizacao().rename(
        columns={
            "Previsão Física 2027": "fisica",
            "Previsão Orçamentária 2027": "valor",
        }
    )
    texto_regionalizacao = json.dumps(_codificar_regionalizacao(regionalizacao), ensure_ascii=False)
    _validar_json_estrito(texto_regionalizacao, SAIDA_REGIONALIZACAO.name)
    SAIDA_REGIONALIZACAO.write_text(texto_regionalizacao, encoding="utf-8")
    print(f"Gerado: {SAIDA_REGIONALIZACAO}")

    # Arquivo separado (carregado só quando a aba QDD é aberta): ~2,4 MB em
    # nível de linha, para os 8 filtros funcionarem no navegador.
    qdd = construir_base_qdd().rename(columns={COLUNA_VALOR_QDD: "valor"})
    texto_qdd = json.dumps({"linhas": qdd.to_dict(orient="records")}, ensure_ascii=False)
    _validar_json_estrito(texto_qdd, SAIDA_QDD.name)
    SAIDA_QDD.write_text(texto_qdd, encoding="utf-8")
    print(f"Gerado: {SAIDA_QDD}")


def _exportar_acao_orcamentaria() -> list[dict]:
    base = construir_base_acao()
    colunas = {
        "uo_label": "uo",
        "acao_label": "acao",
        "programa_label": "programa",
        "Finalidade da Ação": "finalidade",
        "Público-Alvo": "publico_alvo",
        "Identificador de Ação Governamental (IAG)": "iag",
        "Produto": "produto",
        "Unidade de Medida do Produto": "unidade_medida",
    }
    exportado = base.rename(columns=colunas)[list(colunas.values())].copy()
    for ano in ANOS:
        exportado[f"fisica_{ano}"] = base[f"Previsão Física {ano}"].astype(float)
        exportado[f"orcamentaria_{ano}"] = base[f"Previsão Orçamentária {ano}"].astype(float)
    return exportado.to_dict(orient="records")


def _exportar_programa() -> dict:
    base = construir_base_programa()

    programas = []
    for codigo, grupo in base.groupby("Código do Programa"):
        primeira = grupo.iloc[0]
        ods = sorted(
            t for t in grupo["Título do Objetivo de Desenvolvimento Sustentável"].dropna().unique() if t
        )
        programas.append(
            {
                "codigo": codigo,
                "programa": primeira["programa_label"],
                "uo": primeira["uo_label"],
                "area_tematica": primeira["Área Temática"],
                "objetivo": primeira["Objetivo"],
                "ods": ods,
            }
        )

    indicadores = {}
    for programa in programas:
        tabela = construir_tabela_indicadores(programa["codigo"])
        indicadores[programa["codigo"]] = tabela.to_dict(orient="records")

    return {"programas": programas, "indicadores": indicadores}


def _validar_json_estrito(texto: str, nome_arquivo: str) -> None:
    """Garante que o texto não tem NaN/Infinity (extensão do Python que o
    JSON.parse() dos navegadores rejeita — ver docs/premissas.md item 5).
    """

    def rejeitar_constante(constante: str) -> None:
        raise ValueError(
            f"{nome_arquivo} contém a constante não padrão '{constante}', que não é "
            "JSON válido e quebraria o JSON.parse() no navegador. Verifique se há "
            "colunas numéricas com valores ausentes sem .fillna()."
        )

    json.loads(texto, parse_constant=rejeitar_constante)


def _codificar_regionalizacao(df) -> dict:
    def dicionario(coluna: str) -> tuple[list[str], dict[str, int]]:
        valores = sorted(df[coluna].unique())
        return valores, {valor: indice for indice, valor in enumerate(valores)}

    uo_valores, uo_idx = dicionario("uo_label")
    acao_valores, acao_idx = dicionario("acao_label")
    regiao_valores, regiao_idx = dicionario("regiao")
    produto_valores, produto_idx = dicionario("produto")
    unidade_valores, unidade_idx = dicionario("unidade_medida")

    municipios = (
        df[["municipio", "municipio_ibge"]].drop_duplicates().sort_values("municipio")
    )
    municipio_idx = {nome: indice for indice, nome in enumerate(municipios["municipio"])}

    return {
        "uo": uo_valores,
        "acao": acao_valores,
        "regiao": regiao_valores,
        "produto": produto_valores,
        "unidade": unidade_valores,
        "municipios": [
            {"nome": nome, "ibge": ibge}
            for nome, ibge in zip(municipios["municipio"], municipios["municipio_ibge"])
        ],
        "linhas": {
            "uo": df["uo_label"].map(uo_idx).tolist(),
            "acao": df["acao_label"].map(acao_idx).tolist(),
            "regiao": df["regiao"].map(regiao_idx).tolist(),
            "produto": df["produto"].map(produto_idx).tolist(),
            "unidade": df["unidade_medida"].map(unidade_idx).tolist(),
            "municipio": df["municipio"].map(municipio_idx).tolist(),
            "fisica": df["fisica"].tolist(),
            "valor": df["valor"].tolist(),
        },
    }


if __name__ == "__main__":
    gerar()
