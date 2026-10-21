import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import botao_limpar_filtros, botoes_exportar, card_kpi, filtro_selectize
from exportar import csv_bytes, xlsx_bytes
from utils import formatar_bilhoes, formatar_moeda

_NOME_ARQUIVO = "loa_investimentos"


def panel_ui():
    return ui.nav_panel(
        "LOA Investimentos",
        ui.div("LOA Investimentos", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("li_uo", "Unidade Orçamentária", dados.loa_investimentos_uo),
            botao_limpar_filtros("li_limpar"),
            class_="filtros",
        ),
        ui.div(
            ui.output_ui("li_card_receita"),
            ui.output_ui("li_card_despesa"),
            class_="linha-cartoes",
        ),
        ui.div(
            botoes_exportar("li_csv", "li_xlsx"),
            ui.output_data_frame("li_tabela"),
            class_="tabela-card",
        ),
        value="loa_investimentos",
    )


def register_server(input, output, session):
    @reactive.calc
    def receita_filtrada() -> pd.DataFrame:
        df = dados.loa_investimentos_receita
        if input.li_uo():
            df = df[df["uo_label"] == input.li_uo()]
        return df

    @reactive.calc
    def despesa_filtrada() -> pd.DataFrame:
        df = dados.loa_investimentos_despesa
        if input.li_uo():
            df = df[df["uo_label"] == input.li_uo()]
        return df

    @reactive.calc
    def tabela() -> pd.DataFrame:
        agrupado = despesa_filtrada().groupby(["uo_sigla", "acao_label"])["valor"].sum().reset_index()
        agrupado = agrupado.sort_values("valor", ascending=False)
        return pd.DataFrame(
            {
                "Unidade Orçamentária": agrupado["uo_sigla"],
                "Ação Orçamentária": agrupado["acao_label"],
                "LOA 2027 (R$)": agrupado["valor"].map(formatar_moeda),
            }
        )

    @reactive.effect
    @reactive.event(input.li_limpar)
    def _limpar():
        ui.update_selectize("li_uo", selected="")

    @render.ui
    def li_card_receita():
        total = receita_filtrada()["valor"].sum()
        return card_kpi("Receita Total (R$) - 2027", formatar_bilhoes(total))

    @render.ui
    def li_card_despesa():
        total = despesa_filtrada()["valor"].sum()
        return card_kpi("Despesa Total (R$) - 2027", formatar_bilhoes(total))

    @render.data_frame
    def li_tabela():
        return render.DataGrid(tabela(), width="100%", height="420px", summary=False)

    @render.download_button(filename=f"{_NOME_ARQUIVO}.csv")
    def li_csv():
        yield csv_bytes(tabela())

    @render.download_button(filename=f"{_NOME_ARQUIVO}.xlsx")
    def li_xlsx():
        yield xlsx_bytes(tabela())
