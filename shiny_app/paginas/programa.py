import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import botoes_exportar
from exportar import csv_bytes, xlsx_bytes

_NOME_ARQUIVO = "indicadores_programa"
_COLUNAS_TABELA = [
    "Indicador",
    "Periodicidade",
    "Unidade de Medida",
    "Índice de Referência",
    "2027",
    "2028",
    "2029",
    "2030",
]


def panel_ui():
    uos = sorted(dados.programa_programas["uo"].unique())
    nomes = sorted(dados.programa_programas["programa"].unique())
    return ui.nav_panel(
        "Programa",
        ui.div(
            ui.input_selectize("pr_uo", "Unidade Orçamentária", choices=[""] + uos, selected=""),
            ui.input_selectize("pr_programa", "Programa", choices=[""] + nomes, selected=""),
            ui.input_action_button("pr_limpar", "Limpar filtros", class_="btn btn-outline-secondary"),
            class_="filtros",
        ),
        ui.div(
            ui.div("Programa", class_="rotulo"),
            ui.div(ui.output_ui("pr_valor_programa"), class_="valor"),
            class_="acao-card acao-card--destaque",
        ),
        ui.div(
            ui.div(
                ui.div("Unidade Orçamentária", class_="rotulo"),
                ui.div(ui.output_ui("pr_valor_uo"), class_="valor"),
                class_="acao-card",
            ),
            ui.div(
                ui.div("Área Temática", class_="rotulo"),
                ui.div(ui.output_ui("pr_valor_area"), class_="valor"),
                class_="acao-card",
            ),
            style="display:grid;grid-template-columns:3fr 7fr;gap:1rem;",
        ),
        ui.div(
            ui.div(
                ui.div("Objetivo", class_="rotulo"),
                ui.div(ui.output_ui("pr_valor_objetivo"), class_="valor"),
                class_="acao-card",
            ),
            ui.div(
                ui.div(
                    "Objetivo de Desenvolvimento Sustentável - ODS", class_="rotulo"
                ),
                ui.div(ui.output_ui("pr_valor_ods"), class_="valor"),
                class_="acao-card",
            ),
            style="display:grid;grid-template-columns:7fr 3fr;gap:1rem;",
        ),
        ui.h5("Indicadores", class_="mt-3"),
        ui.div(
            botoes_exportar("pr_csv", "pr_xlsx"),
            ui.output_data_frame("pr_tabela"),
            class_="tabela-card",
        ),
        value="programa",
    )


def register_server(input, output, session):
    @reactive.calc
    def programa_selecionado() -> pd.Series:
        df = dados.programa_programas
        filtrado = df
        if input.pr_uo():
            filtrado = filtrado[filtrado["uo"] == input.pr_uo()]
        if input.pr_programa():
            filtrado = filtrado[filtrado["programa"] == input.pr_programa()]
        if filtrado.empty:
            filtrado = df
        return filtrado.sort_values(["uo", "programa"]).iloc[0]

    @reactive.calc
    def tabela_indicadores() -> pd.DataFrame:
        codigo = programa_selecionado()["codigo"]
        df = dados.programa_indicadores
        return df[df["codigo"] == codigo][_COLUNAS_TABELA]

    @reactive.effect
    @reactive.event(input.pr_limpar)
    def _limpar():
        ui.update_selectize("pr_uo", selected="")
        ui.update_selectize("pr_programa", selected="")

    @render.ui
    def pr_valor_programa():
        return programa_selecionado()["programa"]

    @render.ui
    def pr_valor_uo():
        return programa_selecionado()["uo"]

    @render.ui
    def pr_valor_area():
        return programa_selecionado()["area_tematica"]

    @render.ui
    def pr_valor_objetivo():
        return programa_selecionado()["objetivo"]

    @render.ui
    def pr_valor_ods():
        ods = programa_selecionado()["ods"]
        if not ods:
            return ui.p("—")
        return ui.tags.ul(*[ui.tags.li(o) for o in ods], class_="lista-simples")

    @render.data_frame
    def pr_tabela():
        return render.DataGrid(tabela_indicadores(), height="320px", summary=False)

    @render.download_button(filename=f"{_NOME_ARQUIVO}.csv")
    def pr_csv():
        yield csv_bytes(tabela_indicadores())

    @render.download_button(filename=f"{_NOME_ARQUIVO}.xlsx")
    def pr_xlsx():
        yield xlsx_bytes(tabela_indicadores())
