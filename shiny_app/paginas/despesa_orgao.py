import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import card_kpi, filtro_selectize, plotly_html
from graficos import grafico_absoluto_vertical
from utils import formatar_bilhoes, formatar_moeda


def panel_ui():
    uos = sorted(dados.despesa_orgao["uo_label"].unique())
    return ui.nav_panel(
        "Despesa por Órgão",
        ui.div("Despesa por Órgão", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("do_uo", "Unidade Orçamentária", uos),
            ui.input_action_button("do_limpar", "Limpar filtros", class_="btn btn-outline-secondary"),
            class_="filtros",
        ),
        ui.div(
            ui.output_ui("do_card"),
            ui.div(ui.output_ui("do_grafico"), class_="grafico-card"),
            class_="linha-card-grafico",
        ),
        ui.div(
            ui.div(
                ui.h5("Despesa por Ação Orçamentária", class_="lista-cartao-titulo"),
                ui.output_ui("do_lista_acao"),
                class_="lista-cartao",
            ),
            ui.div(
                ui.h5("Despesa por Fonte de Recursos", class_="lista-cartao-titulo"),
                ui.output_ui("do_lista_fonte"),
                class_="lista-cartao",
            ),
            class_="linha-cartoes",
        ),
        value="despesa_orgao",
    )


def _lista_cartao(itens: list[tuple[str, str]]):
    linhas = [
        ui.div(ui.span(label, class_="label"), ui.span(valor, class_="valor"), class_="lista-cartao-item")
        for label, valor in itens
    ]
    return ui.div(*linhas, class_="lista-cartao-corpo")


def register_server(input, output, session):
    @reactive.calc
    def base_filtrada() -> pd.DataFrame:
        df = dados.despesa_orgao
        if input.do_uo():
            df = df[df["uo_label"] == input.do_uo()]
        return df

    @reactive.effect
    @reactive.event(input.do_limpar)
    def _limpar():
        ui.update_selectize("do_uo", selected="")

    @render.ui
    def do_card():
        total = base_filtrada()["valor"].sum()
        return card_kpi("Despesa Total (R$) - 2027", formatar_bilhoes(total))

    @render.ui
    def do_grafico():
        fig = grafico_absoluto_vertical(base_filtrada(), "grupo_despesa_descricao", "valor", "Despesa por Grupo")
        return plotly_html(fig)

    @render.ui
    def do_lista_acao():
        agrupado = base_filtrada().groupby("acao_label")["valor"].sum().sort_values(ascending=False)
        itens = [(label, formatar_moeda(valor)) for label, valor in agrupado.items()]
        return _lista_cartao(itens)

    @render.ui
    def do_lista_fonte():
        agrupado = base_filtrada().groupby("fonte_label")["valor"].sum()
        total = agrupado.sum()
        percentuais = (agrupado / total * 100).sort_values(ascending=False)
        itens = [(label, f"{valor:.1f}%") for label, valor in percentuais.items()]
        return _lista_cartao(itens)
