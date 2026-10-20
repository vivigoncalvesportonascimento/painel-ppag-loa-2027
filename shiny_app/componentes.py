"""Componentes de UI reaproveitados pelas páginas do painel Shiny."""

import faicons
from shiny import ui

_TEMA_CARD = ui.value_box_theme(fg="#ffffff", bg="#0047ab")


def plotly_html(fig) -> ui.HTML:
    """Converte uma figura Plotly em HTML embutível via `@render.ui`.

    Plotly.js é carregado uma única vez (CDN, incluído no <head> do app via
    `plotly_head()`); aqui só o HTML/JS específico da figura é gerado.
    """
    return ui.HTML(
        fig.to_html(
            include_plotlyjs=False,
            full_html=False,
            config={"displayModeBar": False, "responsive": True},
        )
    )


def plotly_head() -> ui.Tag:
    return ui.tags.script(src="https://cdn.plot.ly/plotly-2.35.2.min.js")


def filtro_selectize(
    id: str, label: str, opcoes: list[str], placeholder_vazio: str = "Todas"
) -> ui.Tag:
    """Select com busca (`input_selectize` já busca nativamente, mas precisa
    de 1) um rótulo de texto para a opção em branco — senão ela não aparece
    na lista de opções — e 2) `placeholder` explícito para mostrar
    "Pesquisar" na caixa, como no site estático/Observable).
    """
    escolhas = {"": placeholder_vazio, **{o: o for o in opcoes}}
    return ui.input_selectize(
        id, label, choices=escolhas, selected="", options={"placeholder": "Pesquisar"}
    )


def botoes_exportar(id_csv: str, id_xlsx: str) -> ui.Tag:
    return ui.div(
        ui.download_button(id_csv, "Exportar CSV", class_="botao-exportar"),
        ui.download_button(id_xlsx, "Exportar Excel", class_="botao-exportar"),
        class_="tabela-exportar",
    )


def card_kpi(titulo: str, valor: str, icone: str = "coins") -> ui.Tag:
    """Card de KPI usando o value_box nativo do Shiny (sombra, cor de marca e
    ícone — mais polido que uma div plana), ainda com as classes `valor`/
    `titulo` para os testes e para quem quiser reaproveitar o CSS.
    """
    return ui.value_box(
        ui.span(titulo, class_="titulo"),
        ui.span(valor, class_="valor"),
        showcase=faicons.icon_svg(icone),
        showcase_layout="left center",
        theme=_TEMA_CARD,
        class_="card-kpi",
        full_screen=False,
    )
