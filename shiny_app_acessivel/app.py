"""Painel PPAG-LOA 2027 — versão Shiny for Python / Shinylive (acessível).

Mesmos dados, mesmas regras de negócio e mesma lógica reativa de
`../shiny_app/` — ver ../docs/premissas.md e
../docs/superpowers/specs/2026-10-26-painel-shiny-acessivel-design.md.
Só a camada de apresentação muda: menu lateral em vez de navbar
horizontal, paleta/tipografia novas, toggle "Ver como tabela" em cada
gráfico, foco visível e skip link.
"""

from pathlib import Path

from shiny import App, ui

from componentes import plotly_head, script_limpar_selecao_grafico
from paginas import (
    acao_orcamentaria,
    despesa_fiscal,
    despesa_orgao,
    glossario,
    links_uteis,
    loa_investimentos,
    programa,
    qdd,
    receita_fiscal,
    regionalizacao,
    sobre,
    visao_geral,
)

_PAGINAS = [
    sobre,
    visao_geral,
    acao_orcamentaria,
    programa,
    regionalizacao,
    receita_fiscal,
    despesa_fiscal,
    despesa_orgao,
    qdd,
    loa_investimentos,
    glossario,
    links_uteis,
]

app_ui = ui.page_bootstrap(
    ui.tags.head(
        plotly_head(),
        script_limpar_selecao_grafico(),
        ui.tags.link(rel="preconnect", href="https://fonts.googleapis.com"),
        ui.tags.link(
            rel="stylesheet",
            href=(
                "https://fonts.googleapis.com/css2?"
                "family=Lexend:wght@500;600;700&family=Public+Sans:wght@400;500;600;700&display=swap"
            ),
        ),
        ui.tags.link(rel="stylesheet", href="estilo.css"),
    ),
    ui.tags.a("Pular para o conteúdo", href="#conteudo-principal", class_="skip-link"),
    ui.tags.header(
        ui.span("Painel PPAG-LOA 2027", class_="app-titulo"),
        ui.span("Versão acessível", class_="app-subtitulo"),
        class_="app-cabecalho",
    ),
    ui.div(
        ui.navset_pill_list(
            *[pagina.panel_ui() for pagina in _PAGINAS],
            id="pagina_ativa",
            well=False,
            widths=(2, 10),
        ),
        id="conteudo-principal",
        tabindex="-1",
        class_="app-conteudo",
    ),
    ui.tags.footer(
        ui.hr(),
        ui.p(
            "Construído com Shiny for Python + Shinylive — versão acessível, comparada com o ",
            ui.a(
                "painel publicado no GitHub Pages",
                href="https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/",
                target="_blank",
                rel="noopener noreferrer",
            ),
            " e com a ",
            ui.a(
                "versão Shiny original",
                href="https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/shiny/",
                target="_blank",
                rel="noopener noreferrer",
            ),
            ".",
            class_="text-muted small text-center mb-3",
        ),
    ),
    title="Painel PPAG-LOA 2027 — Acessível",
)


def server(input, output, session):
    for pagina in _PAGINAS:
        pagina.register_server(input, output, session)


app = App(app_ui, server, static_assets={"/": Path(__file__).parent / "www"})
