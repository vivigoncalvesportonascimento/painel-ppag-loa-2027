import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import filtro_selectize, plotly_html
from graficos import grafico_por_ano
from utils import formatar_moeda

_ANOS = [2027, 2028, 2029, 2030]


def panel_ui():
    uos = sorted(dados.acao_orcamentaria["uo"].unique())
    acoes = sorted(dados.acao_orcamentaria["acao"].unique())
    return ui.nav_panel(
        "Ação Orçamentária",
        ui.div("Ação Orçamentária", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("ac_uo", "Unidade Orçamentária", uos, "Selecione..."),
            filtro_selectize("ac_acao", "Ação Orçamentária", acoes, "Selecione..."),
            ui.input_action_button("ac_limpar", "Limpar filtros", class_="btn btn-outline-secondary"),
            class_="filtros",
        ),
        ui.div(
            ui.div("Ação Orçamentária", class_="rotulo"),
            ui.div(ui.output_ui("ac_valor_acao"), class_="valor"),
            class_="acao-card acao-card--destaque",
        ),
        ui.div(
            ui.div(
                ui.div("Unidade Orçamentária", class_="rotulo"),
                ui.div(ui.output_ui("ac_valor_uo"), class_="valor"),
                class_="acao-card",
            ),
            ui.div(
                ui.div("Programa", class_="rotulo"),
                ui.div(ui.output_ui("ac_valor_programa"), class_="valor"),
                class_="acao-card",
            ),
            style="display:grid;grid-template-columns:3fr 7fr;gap:1rem;",
        ),
        ui.div(
            ui.div(
                ui.div("Finalidade da Ação", class_="rotulo"),
                ui.div(ui.output_ui("ac_valor_finalidade"), class_="valor"),
                class_="acao-card",
            ),
            ui.div(
                ui.div("Público-Alvo", class_="rotulo"),
                ui.div(ui.output_ui("ac_valor_publico"), class_="valor"),
                class_="acao-card",
            ),
            style="display:grid;grid-template-columns:7fr 3fr;gap:1rem;",
        ),
        ui.div(
            ui.div(
                ui.div("Identificador de Ação Governamental (IAG)", class_="rotulo"),
                ui.div(ui.output_ui("ac_valor_iag"), class_="valor"),
                class_="acao-card",
            ),
            ui.div(
                ui.div("Produto", class_="rotulo"),
                ui.div(ui.output_ui("ac_valor_produto"), class_="valor"),
                class_="acao-card",
            ),
            ui.div(
                ui.div("Unidade de Medida (Produto)", class_="rotulo"),
                ui.div(ui.output_ui("ac_valor_unidade"), class_="valor"),
                class_="acao-card",
            ),
            style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;",
        ),
        ui.div(
            ui.div(ui.output_ui("ac_grafico_fisica"), class_="grafico-card"),
            ui.div(ui.output_ui("ac_grafico_orcamentaria"), class_="grafico-card"),
            class_="grade-graficos",
        ),
        value="acao_orcamentaria",
    )


def register_server(input, output, session):
    @reactive.calc
    def linha_selecionada() -> pd.Series:
        df = dados.acao_orcamentaria
        filtrado = df
        if input.ac_uo():
            filtrado = filtrado[filtrado["uo"] == input.ac_uo()]
        if input.ac_acao():
            filtrado = filtrado[filtrado["acao"] == input.ac_acao()]
        if filtrado.empty:
            filtrado = df
        return filtrado.sort_values(["uo", "acao"]).iloc[0]

    @reactive.effect
    @reactive.event(input.ac_limpar)
    def _limpar():
        ui.update_selectize("ac_uo", selected="")
        ui.update_selectize("ac_acao", selected="")

    @render.ui
    def ac_valor_acao():
        return linha_selecionada()["acao"]

    @render.ui
    def ac_valor_uo():
        return linha_selecionada()["uo"]

    @render.ui
    def ac_valor_programa():
        return linha_selecionada()["programa"]

    @render.ui
    def ac_valor_finalidade():
        return linha_selecionada()["finalidade"]

    @render.ui
    def ac_valor_publico():
        return linha_selecionada()["publico_alvo"]

    @render.ui
    def ac_valor_iag():
        return linha_selecionada()["iag"]

    @render.ui
    def ac_valor_produto():
        return linha_selecionada()["produto"]

    @render.ui
    def ac_valor_unidade():
        return linha_selecionada()["unidade_medida"]

    @render.ui
    def ac_grafico_fisica():
        linha = linha_selecionada()
        valores = [float(linha[f"fisica_{ano}"]) for ano in _ANOS]
        fig = grafico_por_ano(_ANOS, valores, "Previsão Física", lambda v: f"{v:,.0f}".replace(",", "."))
        return plotly_html(fig)

    @render.ui
    def ac_grafico_orcamentaria():
        linha = linha_selecionada()
        valores = [float(linha[f"orcamentaria_{ano}"]) for ano in _ANOS]
        fig = grafico_por_ano(_ANOS, valores, "Previsão Orçamentária", formatar_moeda)
        return plotly_html(fig)
