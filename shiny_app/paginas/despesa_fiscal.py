from shiny import reactive, render, ui

import dados_app as dados
from componentes import card_kpi, plotly_html, selecao_grafico
from graficos import grafico_absoluto_vertical, grafico_percentual_horizontal
from utils import formatar_bilhoes


def panel_ui():
    return ui.nav_panel(
        "Despesa Fiscal",
        ui.div("Despesa Fiscal", class_="titulo-pagina"),
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
    def _base_excluindo(dimensao_excluida: str | None):
        # Base com as 3 dimensões (poder, grupo, função) na mesma linha --
        # cada gráfico filtra pelas seleções feitas nos OUTROS dois (não na
        # sua própria), para continuar mostrando todas as suas categorias.
        df = dados.despesa_fiscal_detalhe
        poder = selecao_grafico(input, "df_grafico_poder")
        grupo = selecao_grafico(input, "df_grafico_grupo")
        funcao = selecao_grafico(input, "df_grafico_funcao")
        if dimensao_excluida != "poder" and poder:
            df = df[df["uo_poder"] == poder]
        if dimensao_excluida != "grupo" and grupo:
            df = df[df["grupo_despesa_descricao"] == grupo]
        if dimensao_excluida != "funcao" and funcao:
            df = df[df["funcao_descricao"] == funcao]
        return df

    @reactive.calc
    def base_para_card():
        return _base_excluindo(None)

    @reactive.calc
    def base_para_poder():
        return _base_excluindo("poder")

    @reactive.calc
    def base_para_grupo():
        return _base_excluindo("grupo")

    @reactive.calc
    def base_para_funcao():
        return _base_excluindo("funcao")

    @render.ui
    def df_card():
        total = base_para_card()["valor"].sum()
        return card_kpi("Despesa Total (R$) - 2027", formatar_bilhoes(total))

    @render.ui
    def df_grafico_poder():
        fig = grafico_absoluto_vertical(
            base_para_poder(), "uo_poder", "valor", "Despesa por Poder e Reserva de Contingência"
        )
        return plotly_html(fig, id="df_grafico_poder", selecionavel=True)

    @render.ui
    def df_grafico_grupo():
        fig = grafico_percentual_horizontal(
            base_para_grupo(), "grupo_despesa_descricao", "valor", "Despesa por Grupo"
        )
        return plotly_html(fig, id="df_grafico_grupo", selecionavel=True)

    @render.ui
    def df_grafico_funcao():
        fig = grafico_percentual_horizontal(
            base_para_funcao(), "funcao_descricao", "valor", "Despesa por Função"
        )
        return plotly_html(fig, id="df_grafico_funcao", selecionavel=True)
