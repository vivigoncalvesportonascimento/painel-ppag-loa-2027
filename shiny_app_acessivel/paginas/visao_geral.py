from shiny import reactive, render, ui

import dados_app as dados
from componentes import botao_limpar_filtros, card_kpi, limpar_selecao_graficos, plotly_html, selecao_grafico
from graficos import grafico_percentual_horizontal
from utils import formatar_bilhoes


def panel_ui():
    return ui.nav_panel(
        "Visão Geral",
        ui.div("Visão Geral", class_="titulo-pagina"),
        ui.p("Dados gerais do orçamento 2027", class_="text-muted"),
        ui.div(botao_limpar_filtros("vg_limpar"), class_="filtros"),
        ui.output_ui("vg_cards"),
        ui.div(
            ui.div(ui.output_ui("vg_grafico_area"), class_="grafico-card"),
            ui.div(ui.output_ui("vg_grafico_setor"), class_="grafico-card"),
            class_="grade-graficos",
        ),
        value="visao_geral",
    )


def register_server(input, output, session):
    @reactive.effect
    @reactive.event(input.vg_limpar)
    async def _limpar():
        await limpar_selecao_graficos(session, "vg_grafico_area", "vg_grafico_setor")

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

    @reactive.calc
    def _base_para_area():
        # O gráfico de Área Temática reflete a seleção feita no de Setor de
        # Governo (e vice-versa), mas nenhum dos dois se autofiltra -- cada
        # um continua mostrando todas as suas próprias categorias.
        df = dados.visao_geral
        setor = selecao_grafico(input, "vg_grafico_setor")
        if setor:
            df = df[df["setor_governo"] == setor]
        return df

    @reactive.calc
    def _base_para_setor():
        df = dados.visao_geral
        area = selecao_grafico(input, "vg_grafico_area")
        if area:
            df = df[df["area_tematica"] == area]
        return df

    @render.ui
    def vg_grafico_area():
        fig = grafico_percentual_horizontal(
            _base_para_area(), "area_tematica", "valor", "Previsão 2027 por Área Temática"
        )
        return plotly_html(fig, id="vg_grafico_area", selecionavel=True)

    @render.ui
    def vg_grafico_setor():
        fig = grafico_percentual_horizontal(
            _base_para_setor(), "setor_governo", "valor", "Previsão 2027 por Setor de Governo"
        )
        return plotly_html(fig, id="vg_grafico_setor", selecionavel=True)
