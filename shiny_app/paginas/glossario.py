from shiny import reactive, render, ui

import dados_app as dados

_TERMOS = dados.glossario


def panel_ui():
    botoes = [
        ui.input_action_button(
            f"gl_termo_{i}",
            t["termo"],
            class_="btn btn-sm rounded-pill btn-outline-secondary termo-botao",
        )
        for i, t in enumerate(_TERMOS)
    ]
    return ui.nav_panel(
        "Glossário",
        ui.div(*botoes, class_="glossario-nuvem"),
        ui.div(ui.h6("Definição Técnica"), ui.output_ui("gl_tecnica"), class_="glossario-painel"),
        ui.div(ui.h6("Linguagem Simples"), ui.output_ui("gl_simples"), class_="glossario-painel"),
        value="glossario",
    )


def register_server(input, output, session):
    selecionado = reactive.Value(0)

    def _registrar_handler(indice: int):
        @reactive.effect
        @reactive.event(getattr(input, f"gl_termo_{indice}"))
        def _handler():
            selecionado.set(indice)

    for i in range(len(_TERMOS)):
        _registrar_handler(i)

    @render.ui
    def gl_tecnica():
        return ui.p(_TERMOS[selecionado()]["definicao_tecnica"])

    @render.ui
    def gl_simples():
        return ui.p(_TERMOS[selecionado()]["linguagem_simples"])
