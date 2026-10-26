"""Painel PPAG-LOA 2027 — versão Shiny for Python / Shinylive.

Mesmos dados, mesmas regras de negócio e mesmas funcionalidades (filtros,
gráficos, mapa, tabelas com exportação CSV/Excel) da versão em site
estático — ver ../docs/premissas.md.
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

# Sem `theme=` explícito: o Shiny usa o preset "shiny" (CSS pré-compilado,
# servido como arquivo estático) por padrão. Qualquer `ui.Theme(...)`
# dispara compilação SASS via libsass, indisponível no Pyodide/Shinylive —
# a cor de marca é sobreposta via variáveis CSS do Bootstrap em
# www/estilo.css em vez disso.

app_ui = ui.page_navbar(
    *[pagina.panel_ui() for pagina in _PAGINAS],
    title="Painel PPAG-LOA 2027",
    header=ui.tags.head(
        plotly_head(),
        script_limpar_selecao_grafico(),
        ui.tags.link(rel="stylesheet", href="estilo.css"),
    ),
    footer=ui.div(
        ui.hr(),
        ui.p(
            "Construído com Shiny for Python + Shinylive — versão de comparação do ",
            ui.a(
                "painel publicado no GitHub Pages",
                href="https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/",
                target="_blank",
                rel="noopener noreferrer",
            ),
            ".",
            class_="text-muted small text-center mb-3",
        ),
    ),
)


def server(input, output, session):
    for pagina in _PAGINAS:
        pagina.register_server(input, output, session)


app = App(app_ui, server, static_assets={"/": Path(__file__).parent / "www"})
