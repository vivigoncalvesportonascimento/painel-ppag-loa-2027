"""Cálculos da página "Regionalização", compartilhados entre o app
Streamlit e o gerador do site estático (GitHub Pages).

`construir_base_enriquecida` junta localizadores_todos_planejamento.txt
com acoes_planejamento.txt (para trazer Produto / Unidade de Medida) pela
combinação "Código da UO Responsável pela Ação" + "Código da Ação" — a
chave precisa normalizar o código da UO, que vem com zero à esquerda em
localizadores ("01261") mas sem zero em ações ("1261") (ver
docs/premissas.md). O filtro de Município nunca restringe a base usada
pelo mapa (só o destaque de cor) — os outros 4 filtros (UO, Ação, Região,
Produto) restringem tanto o mapa quanto a tabela.
"""

import pandas as pd
import plotly.graph_objects as go

from etl.limpeza_inicial import carregar_acoes, carregar_localizadores
from etl.regionalizacao import carregar_geojson_municipios
from utils import formatar_moeda

COLUNA_VALOR = "Previsão Orçamentária 2027"
COLUNA_FISICA = "Previsão Física 2027"

_COR_SEM_DESTAQUE = "#cbd2d9"
_COR_DESTAQUE = "#0047ab"


def construir_base_enriquecida() -> pd.DataFrame:
    loc = carregar_localizadores().copy()
    ac = carregar_acoes().copy()

    coluna_uo = "Código da Unidade Orçamentária Responsável pela Ação"
    loc["uo_norm"] = loc[coluna_uo].astype(int).astype(str)
    ac["uo_norm"] = ac[coluna_uo].astype(int).astype(str)

    base = loc.merge(
        ac[["uo_norm", "Código da Ação", "Produto", "Unidade de Medida do Produto"]],
        on=["uo_norm", "Código da Ação"],
        how="left",
    )

    return pd.DataFrame(
        {
            "uo_label": base["uo_norm"] + " - " + base["Unidade Orçamentária Responsável pela Ação"],
            "acao_label": base["Código da Ação"] + " - " + base["Título da Ação"],
            "regiao": base["Região Geográfica Intermediária"],
            "municipio": base["Município"],
            "municipio_ibge": base["Código do Município IBGE"],
            "produto": base["Produto"].fillna(""),
            "unidade_medida": base["Unidade de Medida do Produto"].fillna(""),
            COLUNA_FISICA: pd.to_numeric(base[COLUNA_FISICA]),
            COLUNA_VALOR: pd.to_numeric(base[COLUNA_VALOR]),
        }
    )


def construir_listas_filtro(base: pd.DataFrame) -> dict:
    return {
        "uo": sorted(base["uo_label"].unique()),
        "acao": sorted(base["acao_label"].unique()),
        "regiao": sorted(base["regiao"].dropna().unique()),
        "municipio": sorted(base["municipio"].dropna().unique()),
        "produto": sorted(p for p in base["produto"].unique() if p),
    }


def construir_tabela(base: pd.DataFrame) -> pd.DataFrame:
    agrupado = (
        base.groupby(["acao_label", "produto", "unidade_medida", "regiao", "municipio"])[
            [COLUNA_FISICA, COLUNA_VALOR]
        ]
        .sum()
        .reset_index()
    )
    agrupado = agrupado.sort_values(COLUNA_VALOR, ascending=False)

    return pd.DataFrame(
        {
            "Ação Orçamentária": agrupado["acao_label"],
            "Produto": agrupado["produto"],
            "Unidade de Medida": agrupado["unidade_medida"],
            "Região Geográfica Intermediária": agrupado["regiao"],
            "Município": agrupado["municipio"],
            "Previsão Física 2027": agrupado[COLUNA_FISICA].map(lambda v: f"{v:,.0f}".replace(",", ".")),
            "Previsão Orçamentária 2027": agrupado[COLUNA_VALOR].map(formatar_moeda),
        }
    ).reset_index(drop=True)


def construir_mapa(base_mapa: pd.DataFrame, municipios_selecionados: list[str]) -> "go.Figure":
    geojson = carregar_geojson_municipios()
    universo = pd.DataFrame(
        {
            "municipio_ibge": [f["properties"]["id"] for f in geojson["features"]],
            "municipio_geo": [f["properties"]["name"] for f in geojson["features"]],
        }
    )

    valores = (
        base_mapa.groupby(["municipio", "municipio_ibge"])[COLUNA_VALOR].sum().reset_index()
    )

    dados_mapa = universo.merge(valores, on="municipio_ibge", how="left")
    dados_mapa[COLUNA_VALOR] = dados_mapa[COLUNA_VALOR].fillna(0)
    dados_mapa["municipio"] = dados_mapa["municipio"].fillna(dados_mapa["municipio_geo"])

    ibges_selecionados = set(
        base_mapa.loc[base_mapa["municipio"].isin(municipios_selecionados), "municipio_ibge"]
    )
    dados_mapa["destaque"] = dados_mapa["municipio_ibge"].isin(ibges_selecionados).astype(int)
    dados_mapa["valor_formatado"] = dados_mapa[COLUNA_VALOR].map(formatar_moeda)

    fig = go.Figure(
        go.Choropleth(
            geojson=geojson,
            featureidkey="properties.id",
            locations=dados_mapa["municipio_ibge"],
            z=dados_mapa["destaque"],
            zmin=0,
            zmax=1,
            colorscale=[[0, _COR_SEM_DESTAQUE], [1, _COR_DESTAQUE]],
            showscale=False,
            marker_line_color="#ffffff",
            marker_line_width=0.4,
            customdata=dados_mapa[["municipio", "valor_formatado"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Previsão Orçamentária 2027: %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        height=560,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui, -apple-system, Segoe UI, Arial, sans-serif", color="#1f2933"),
    )
    return fig
