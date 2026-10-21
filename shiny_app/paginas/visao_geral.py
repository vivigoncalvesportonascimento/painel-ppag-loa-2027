from shiny import render, ui

import dados_app as dados
from componentes import card_kpi, plotly_html
from graficos import grafico_percentual_horizontal
from utils import formatar_bilhoes


def panel_ui():
    return ui.nav_panel(
        "Visão Geral",
        ui.div("Visão Geral", class_="titulo-pagina"),
        ui.p("Dados gerais do orçamento 2027", class_="text-muted"),
        ui.output_ui("vg_cards"),
        ui.div(
            ui.div(ui.output_ui("vg_grafico_area"), class_="grafico-card"),
            ui.div(ui.output_ui("vg_grafico_setor"), class_="grafico-card"),
            class_="grade-graficos",
        ),
        value="visao_geral",
    )


def register_server(input, output, session):
    @render.ui
    def vg_cards():
        c = dados.cards
        itens = [
            ("Previsão 2027 - Orçamento Fiscal", formatar_bilhoes(c["total_fiscal"])),
            ("Previsão 2027 - Orçamento de Investimentos", formatar_bilhoes(c["total_investimento"])),
            ("Quantidade de Programas", f"{int(c['qtd_programas']):,}".replace(",", ".")),
            ("Quantidade de Ações", f"{int(c['qtd_acoes']):,}".replace(",", ".")),
            ("Projetos Estratégicos", f"{int(c['qtd_projetos_estrategicos']):,}".replace(",", ".")),
        ]
        return ui.div(
            *[card_kpi(titulo, valor, icone=None, compacto=True) for titulo, valor in itens],
            class_="grade-cards",
        )

    @render.ui
    def vg_grafico_area():
        fig = grafico_percentual_horizontal(
            dados.visao_geral, "area_tematica", "valor", "Previsão 2027 por Área Temática"
        )
        return plotly_html(fig)

    @render.ui
    def vg_grafico_setor():
        fig = grafico_percentual_horizontal(
            dados.visao_geral, "setor_governo", "valor", "Previsão 2027 por Setor de Governo"
        )
        return plotly_html(fig)
