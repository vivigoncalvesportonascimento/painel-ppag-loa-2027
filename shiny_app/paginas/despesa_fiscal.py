from shiny import render, ui

import dados_app as dados
from componentes import card_kpi, plotly_html
from graficos import grafico_absoluto_vertical, grafico_percentual_horizontal
from utils import formatar_bilhoes


def panel_ui():
    return ui.nav_panel(
        "Despesa Fiscal",
        ui.div(
            ui.output_ui("df_card"),
            ui.div(ui.output_ui("df_grafico_poder"), class_="grafico-card"),
            class_="linha-card-grafico",
        ),
        ui.div(
            ui.div(ui.output_ui("df_grafico_grupo"), class_="grafico-card"),
            ui.div(ui.output_ui("df_grafico_funcao"), class_="grafico-card"),
            class_="grade-graficos",
        ),
        value="despesa_fiscal",
    )


def register_server(input, output, session):
    @render.ui
    def df_card():
        return card_kpi("Despesa Total (R$) - 2027", formatar_bilhoes(dados.despesa_fiscal_card_total))

    @render.ui
    def df_grafico_poder():
        fig = grafico_absoluto_vertical(
            dados.despesa_fiscal_poder, "uo_poder", "valor", "Despesa por Poder e Reserva de Contingência"
        )
        return plotly_html(fig)

    @render.ui
    def df_grafico_grupo():
        fig = grafico_percentual_horizontal(
            dados.despesa_fiscal_grupo, "grupo_despesa_descricao", "valor", "Despesa por Grupo"
        )
        return plotly_html(fig)

    @render.ui
    def df_grafico_funcao():
        fig = grafico_percentual_horizontal(
            dados.despesa_fiscal_funcao, "funcao_descricao", "valor", "Despesa por Função"
        )
        return plotly_html(fig)
