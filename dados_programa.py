"""Cálculos da página "Programa", usados pelo gerador do site estático
(GitHub Pages).

Página de detalhe: os dois filtros (UO, Programa) selecionam um único
programa. A maioria dos campos é invariante dentro do programa (um
programa pertence a uma única UO), exceto o Objetivo de Desenvolvimento
Sustentável (ODS), que pode ter vários valores distintos para o mesmo
programa — por isso vem como lista no card 5.

O código do programa tem zero à esquerda em ambas as bases
(programas_planejamento.txt e indicadores_planejamento.txt, no mesmo
formato nas duas) — usado como está para o cruzamento, mas sem o zero à
esquerda no rótulo exibido (ex.: "22 - ..." em vez de "0022 - ...").
"""

import pandas as pd

from etl.limpeza_inicial import carregar_indicadores, carregar_programas


def construir_base_enriquecida() -> pd.DataFrame:
    df = carregar_programas().copy()
    df["codigo_programa_label"] = df["Código do Programa"].astype(int).astype(str)
    df["uo_label"] = (
        df["Código da Unidade Orçamentária Responsável pelo Programa"]
        + " - "
        + df["Unidade Orçamentária Responsável pelo Programa"]
    )
    df["programa_label"] = df["codigo_programa_label"] + " - " + df["Nome do Programa"]
    return df


def construir_listas_filtro(base: pd.DataFrame) -> dict:
    return {
        "uo": sorted(base["uo_label"].unique()),
        "programa": sorted(base["programa_label"].unique()),
    }


def selecionar_programa(base: pd.DataFrame, uo_label: str, programa_label: str) -> pd.DataFrame:
    """Retorna todas as linhas do programa selecionado (mais de uma linha
    por causa dos múltiplos ODS possíveis)."""
    filtrado = base
    if uo_label:
        filtrado = filtrado[filtrado["uo_label"] == uo_label]
    if programa_label:
        filtrado = filtrado[filtrado["programa_label"] == programa_label]
    if filtrado.empty:
        filtrado = base

    programa_escolhido = filtrado.sort_values(["uo_label", "programa_label"])["programa_label"].iloc[0]
    return base[base["programa_label"] == programa_escolhido]


def construir_cards(linhas_programa: pd.DataFrame) -> dict:
    primeira = linhas_programa.iloc[0]
    ods_lista = sorted(
        titulo
        for titulo in linhas_programa["Título do Objetivo de Desenvolvimento Sustentável"].dropna().unique()
        if titulo
    )
    return {
        "codigo_programa": primeira["Código do Programa"],
        "programa": primeira["programa_label"],
        "uo": primeira["uo_label"],
        "area_tematica": primeira["Área Temática"],
        "objetivo": primeira["Objetivo"],
        "ods": ods_lista,
    }


def construir_tabela_indicadores(codigo_programa: str) -> pd.DataFrame:
    ind = carregar_indicadores()
    linhas = ind[ind["Código do Programa"] == codigo_programa]

    tabela = pd.DataFrame(
        {
            "Indicador": linhas["Indicador"],
            "Periodicidade": linhas["Periodicidade"],
            "Unidade de Medida": linhas["Unidade de Medida"],
            "Índice de Referência": linhas["Índice de Referência"],
            "2027": linhas["Previsão para 2027"],
            "2028": linhas["Previsão para 2028"],
            "2029": linhas["Previsão para 2029"],
            "2030": linhas["Previsão para 2030"],
        }
    )
    return tabela.fillna("").reset_index(drop=True)
