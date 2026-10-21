import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import botao_limpar_filtros, botoes_exportar, card_kpi, filtro_selectize, plotly_html
from exportar import csv_bytes, xlsx_bytes
from graficos import grafico_absoluto_horizontal
from utils import formatar_bilhoes, formatar_moeda

_NOME_ARQUIVO = "receita_fiscal_uo_fonte"


def panel_ui():
    uos = sorted(dados.receita_fiscal["UO"].unique())
    fontes = sorted(dados.receita_fiscal["fonte_de_recursos"].unique())
    return ui.nav_panel(
        "Receita Fiscal",
        ui.div("Receita Fiscal", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("rf_uo", "UO", uos),
            filtro_selectize("rf_fonte", "Fonte de Recursos", fontes),
            botao_limpar_filtros("rf_limpar"),
            class_="filtros",
        ),
        ui.div(
            ui.output_ui("rf_card"),
            ui.div(ui.output_ui("rf_grafico"), class_="grafico-card"),
            class_="linha-card-grafico",
        ),
        ui.div(
            botoes_exportar("rf_csv", "rf_xlsx"),
            ui.output_data_frame("rf_tabela"),
            class_="tabela-card",
        ),
        value="receita_fiscal",
    )


def register_server(input, output, session):
    @reactive.calc
    def linhas_filtradas() -> pd.DataFrame:
        df = dados.receita_fiscal
        if input.rf_uo():
            df = df[df["UO"] == input.rf_uo()]
        if input.rf_fonte():
            df = df[df["fonte_de_recursos"] == input.rf_fonte()]
        return df

    @reactive.calc
    def tabela_uo_fonte() -> pd.DataFrame:
        agrupado = linhas_filtradas().groupby(["UO", "fonte_de_recursos"])["valor"].sum().reset_index()
        agrupado = agrupado.sort_values("valor", ascending=False)
        return pd.DataFrame(
            {
                "UO": agrupado["UO"],
                "Fonte de Recursos": agrupado["fonte_de_recursos"],
                "LOA 2027 (R$)": agrupado["valor"].map(formatar_moeda),
            }
        )

    @reactive.effect
    @reactive.event(input.rf_limpar)
    def _limpar():
        ui.update_selectize("rf_uo", selected="")
        ui.update_selectize("rf_fonte", selected="")

    @render.ui
    def rf_card():
        total = linhas_filtradas()["valor"].sum()
        return card_kpi("Receita Total (R$) - 2027", formatar_bilhoes(total))

    @render.ui
    def rf_grafico():
        fig = grafico_absoluto_horizontal(
            linhas_filtradas(), "categoria_receita_desc", "valor", "Receitas por Categoria Econômica"
        )
        return plotly_html(fig)

    @render.data_frame
    def rf_tabela():
        return render.DataGrid(tabela_uo_fonte(), width="100%", height="420px", summary=False)

    @render.download_button(filename=f"{_NOME_ARQUIVO}.csv", label="Exportar CSV")
    def rf_csv():
        yield csv_bytes(tabela_uo_fonte())

    @render.download_button(filename=f"{_NOME_ARQUIVO}.xlsx", label="Exportar Excel")
    def rf_xlsx():
        yield xlsx_bytes(tabela_uo_fonte())
