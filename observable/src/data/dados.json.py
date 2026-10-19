"""Data loader do Observable Framework: consolida os dados das páginas sem
mapa/tabela gigante (essas duas, Regionalização e QDD, têm loaders próprios
porque são pesadas e carregadas só quando a página é aberta).

Reaproveita diretamente os módulos dados_*.py / etl/*.py da raiz do
repositório (mesma lógica e premissas usadas por site_estatico/), só muda o
formato de saída: aqui é JSON "cru" (linhas), e a agregação/filtragem roda
no JavaScript da página, igual ao script.js do site estático.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import _repo  # noqa: F401  (ajusta sys.path para a raiz do repo)

from etl.despesa import (
    carregar_auxiliar_funcao,
    carregar_auxiliar_grupo_despesa,
    carregar_auxiliar_poder,
)
from etl.orcamento import carregar_qdd_fiscal, carregar_qdd_investimento
from etl.limpeza_inicial import carregar_acoes, carregar_programas
from dados_acao_orcamentaria import ANOS, construir_base_enriquecida as construir_base_acao
from dados_despesa_fiscal import COLUNA_VALOR as COLUNA_VALOR_DESPESA_FISCAL
from dados_despesa_orgao import COLUNA_VALOR as COLUNA_VALOR_DESPESA_ORGAO
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
from dados_receita_fiscal import COLUNA_VALOR as COLUNA_VALOR_RECEITA
from dados_receita_fiscal import construir_base_enriquecida as construir_base_receita_fiscal
from dados_visao_geral import COLUNA_IAG, COLUNA_PREVISAO_2027

COLUNA_PROGRAMA = "Código do Programa"


def cards() -> dict:
    total_fiscal = carregar_qdd_fiscal()[COLUNA_VALOR_DESPESA_FISCAL].sum()
    total_investimento = carregar_qdd_investimento()["VALOR (R$)"].sum()
    qtd_programas = carregar_programas()[COLUNA_PROGRAMA].nunique()
    acoes = carregar_acoes()
    return {
        "total_fiscal": float(total_fiscal),
        "total_investimento": float(total_investimento),
        "qtd_programas": int(qtd_programas),
        "qtd_acoes": int(len(acoes)),
        "qtd_projetos_estrategicos": int(len(acoes[acoes[COLUNA_IAG] == "1"])),
    }


def visao_geral_linhas() -> list[dict]:
    acoes = carregar_acoes().copy()
    acoes[COLUNA_PREVISAO_2027] = acoes[COLUNA_PREVISAO_2027].astype(float)
    acoes["Área Temática"] = acoes["Área Temática"].str.upper()
    exportado = acoes.rename(
        columns={
            "Área Temática": "area_tematica",
            "Setor de Governo": "setor_governo",
            COLUNA_PREVISAO_2027: "valor",
        }
    )[["area_tematica", "setor_governo", "valor"]]
    return exportado.to_dict(orient="records")


def despesa_fiscal() -> dict:
    despesa = carregar_qdd_fiscal()
    poder = despesa.merge(carregar_auxiliar_poder(), left_on="COD_UO", right_on="uo_cod")
    grupo = despesa.merge(
        carregar_auxiliar_grupo_despesa(), left_on="GRUPO_DESPESA", right_on="grupo_despesa_cod"
    )
    funcao = despesa.merge(carregar_auxiliar_funcao(), left_on="FUNCAO", right_on="funcao_cod")
    return {
        "card_total": float(despesa[COLUNA_VALOR_DESPESA_FISCAL].sum()),
        "linhas_poder": poder.rename(columns={COLUNA_VALOR_DESPESA_FISCAL: "valor"})[
            ["uo_poder", "valor"]
        ].to_dict(orient="records"),
        "linhas_grupo": grupo.rename(columns={COLUNA_VALOR_DESPESA_FISCAL: "valor"})[
            ["grupo_despesa_descricao", "valor"]
        ].to_dict(orient="records"),
        "linhas_funcao": funcao.rename(columns={COLUNA_VALOR_DESPESA_FISCAL: "valor"})[
            ["funcao_descricao", "valor"]
        ].to_dict(orient="records"),
    }


def acao_orcamentaria_linhas() -> list[dict]:
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


def programa() -> dict:
    base = construir_base_programa()
    programas = []
    for codigo, grupo in base.groupby(COLUNA_PROGRAMA):
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
    indicadores = {p["codigo"]: construir_tabela_indicadores(p["codigo"]).to_dict(orient="records") for p in programas}
    return {"programas": programas, "indicadores": indicadores}


dados = {
    "cards": cards(),
    "visao_geral": {"linhas": visao_geral_linhas()},
    "despesa_fiscal": despesa_fiscal(),
    "acao_orcamentaria": {"linhas": acao_orcamentaria_linhas()},
    "programa": programa(),
    "receita_fiscal": {
        "linhas": construir_base_receita_fiscal()
        .rename(columns={COLUNA_VALOR_RECEITA: "valor"})
        .to_dict(orient="records")
    },
    "despesa_orgao": {
        "linhas": construir_base_despesa_orgao()
        .rename(columns={COLUNA_VALOR_DESPESA_ORGAO: "valor"})
        .to_dict(orient="records")
    },
    "loa_investimentos": {
        "uo_opcoes": construir_lista_uo_investimentos(),
        "linhas_receita": construir_base_investimentos_receita().to_dict(orient="records"),
        "linhas_despesa": construir_base_investimentos_despesa().to_dict(orient="records"),
    },
    "glossario": construir_lista_termos(),
}


def rejeitar_constante(constante: str) -> None:
    raise ValueError(f"valor nao serializavel em JSON: {constante}")


texto = json.dumps(dados, ensure_ascii=False)
json.loads(texto, parse_constant=rejeitar_constante)  # garante ausencia de NaN/Infinity
sys.stdout.buffer.write(texto.encode("utf-8"))
