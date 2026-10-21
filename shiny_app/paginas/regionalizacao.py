import pandas as pd
import plotly.graph_objects as go
from shiny import reactive, render, ui

import dados_app as dados
from componentes import botao_limpar_filtros, botoes_exportar, filtro_selectize, plotly_html
from exportar import csv_bytes, xlsx_bytes
from utils import formatar_moeda

_NOME_ARQUIVO = "regionalizacao"
_LIMITE_TABELA = 2000
_COR_SEM_DESTAQUE = "#cbd2d9"
_COR_DESTAQUE = "#0047ab"


def panel_ui():
    df = dados.regionalizacao
    uos = sorted(df["uo_label"].unique())
    acoes = sorted(df["acao_label"].unique())
    regioes = sorted(df["regiao"].dropna().unique())
    municipios = sorted(df["municipio"].dropna().unique())
    produtos = sorted(p for p in df["produto"].unique() if p)

    return ui.nav_panel(
        "Regionalização",
        ui.div("Regionalização", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("rg_uo", "Unidade Orçamentária", uos),
            filtro_selectize("rg_acao", "Ação Orçamentária", acoes),
            filtro_selectize("rg_regiao", "Região Geográfica Intermediária", regioes),
            filtro_selectize("rg_municipio", "Município", municipios, "Todos"),
            filtro_selectize("rg_produto", "Produto", produtos, "Todos"),
            botao_limpar_filtros("rg_limpar"),
            class_="filtros",
        ),
        ui.div(ui.output_ui("rg_mapa"), class_="mapa-card"),
        ui.output_ui("rg_aviso"),
        ui.div(
            botoes_exportar("rg_csv", "rg_xlsx"),
            ui.output_data_frame("rg_tabela"),
            class_="tabela-card",
        ),
        value="regionalizacao",
    )


def _aplicar_filtros(input, ignorar_municipio: bool) -> pd.DataFrame:
    df = dados.regionalizacao
    if input.rg_uo():
        df = df[df["uo_label"] == input.rg_uo()]
    if input.rg_acao():
        df = df[df["acao_label"] == input.rg_acao()]
    if input.rg_regiao():
        df = df[df["regiao"] == input.rg_regiao()]
    if input.rg_produto():
        df = df[df["produto"] == input.rg_produto()]
    if not ignorar_municipio and input.rg_municipio():
        df = df[df["municipio"] == input.rg_municipio()]
    return df


def register_server(input, output, session):
    @reactive.effect
    @reactive.event(input.rg_limpar)
    def _limpar():
        ui.update_selectize("rg_uo", selected="")
        ui.update_selectize("rg_acao", selected="")
        ui.update_selectize("rg_regiao", selected="")
        ui.update_selectize("rg_municipio", selected="")
        ui.update_selectize("rg_produto", selected="")

    @reactive.calc
    def base_sem_municipio() -> pd.DataFrame:
        return _aplicar_filtros(input, ignorar_municipio=True)

    @reactive.calc
    def base_tabela() -> pd.DataFrame:
        return _aplicar_filtros(input, ignorar_municipio=False)

    @reactive.calc
    def tabela_agrupada() -> pd.DataFrame:
        agrupado = (
            base_tabela()
            .groupby(["acao_label", "produto", "unidade_medida", "regiao", "municipio"])[
                ["fisica", "valor"]
            ]
            .sum()
            .reset_index()
        )
        return agrupado.sort_values("valor", ascending=False)

    @reactive.calc
    def tabela_formatada() -> pd.DataFrame:
        agrupado = tabela_agrupada().head(_LIMITE_TABELA)
        return pd.DataFrame(
            {
                "Ação Orçamentária": agrupado["acao_label"],
                "Produto": agrupado["produto"],
                "Unidade de Medida": agrupado["unidade_medida"],
                "Região Geográfica Intermediária": agrupado["regiao"],
                "Município": agrupado["municipio"],
                "Previsão Física 2027": agrupado["fisica"].map(lambda v: f"{v:,.0f}".replace(",", ".")),
                "Previsão Orçamentária 2027": agrupado["valor"].map(formatar_moeda),
            }
        )

    @render.ui
    def rg_aviso():
        total = len(tabela_agrupada())
        if total > _LIMITE_TABELA:
            return ui.p(
                f"Mostrando as {_LIMITE_TABELA} linhas de maior valor, de um total de "
                f"{total}. Use os filtros para refinar.",
                class_="text-muted",
            )
        return ui.div()

    @render.ui
    def rg_mapa():
        linhas = base_sem_municipio()
        valores_por_ibge = linhas.groupby("municipio_ibge")["valor"].sum()
        municipio_sel = input.rg_municipio()
        ibge_sel = None
        if municipio_sel:
            correspondentes = linhas.loc[linhas["municipio"] == municipio_sel, "municipio_ibge"]
            if len(correspondentes):
                ibge_sel = correspondentes.iloc[0]

        geojson = dados.mg_municipios_geojson
        ibges = [f["properties"]["id"] for f in geojson["features"]]
        nomes = [f["properties"]["name"] for f in geojson["features"]]
        z = [1 if ibge == ibge_sel else 0 for ibge in ibges]
        textos_valor = [formatar_moeda(valores_por_ibge.get(ibge, 0)) for ibge in ibges]

        fig = go.Figure(
            go.Choropleth(
                geojson=geojson,
                featureidkey="properties.id",
                locations=ibges,
                z=z,
                zmin=0,
                zmax=1,
                colorscale=[[0, _COR_SEM_DESTAQUE], [1, _COR_DESTAQUE]],
                showscale=False,
                marker_line_color="#ffffff",
                marker_line_width=0.4,
                customdata=list(zip(nomes, textos_valor)),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>Previsão Orçamentária 2027: %{customdata[1]}<extra></extra>"
                ),
            )
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            height=540,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="system-ui, -apple-system, Segoe UI, Arial, sans-serif", color="#1f2933"),
        )
        return plotly_html(fig)

    @render.data_frame
    def rg_tabela():
        return render.DataGrid(tabela_formatada(), width="100%", height="440px", summary=False)

    @render.download_button(filename=f"{_NOME_ARQUIVO}.csv")
    def rg_csv():
        yield csv_bytes(tabela_formatada())

    @render.download_button(filename=f"{_NOME_ARQUIVO}.xlsx")
    def rg_xlsx():
        yield xlsx_bytes(tabela_formatada())
