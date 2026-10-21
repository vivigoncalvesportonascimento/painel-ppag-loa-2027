"""Componentes de UI reaproveitados pelas páginas do painel Shiny."""

import faicons
from shiny import reactive, ui

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


def escolhas_filtro(opcoes: list[str], placeholder_vazio: str = "Todas") -> dict[str, str]:
    """Monta o dict de `choices` de um `input_selectize`, com rótulo de texto
    na opção em branco (senão ela não aparece na lista de opções).
    """
    return {"": placeholder_vazio, **{o: o for o in opcoes}}


def filtro_selectize(
    id: str, label: str, opcoes: list[str], placeholder_vazio: str = "Todas"
) -> ui.Tag:
    """Select com busca (`input_selectize` já busca nativamente, mas precisa
    de `placeholder` explícito para mostrar "Pesquisar" na caixa, como no
    site estático/Observable).
    """
    return ui.input_selectize(
        id,
        label,
        choices=escolhas_filtro(opcoes, placeholder_vazio),
        selected="",
        options={"placeholder": "Pesquisar"},
    )


def registrar_filtros_cruzados(input, df, filtros: list[tuple[str, str, str]]) -> None:
    """Registra o efeito "crossfilter" entre os filtros de uma página:
    selecionar uma opção em qualquer um deles restringe as opções
    disponíveis nos demais — e vice-versa, não importa por qual filtro o
    usuário começa (ex.: selecionar a UO 1271 faz a Ação Orçamentária só
    oferecer as ações daquela UO; selecionar antes a ação 1004 faz a UO só
    oferecer a UO 1511, dona daquela ação).

    `filtros` é uma lista de tuplas (id_do_input, nome_da_coluna,
    placeholder_quando_vazio), uma por filtro da página.
    """

    @reactive.effect
    def _crossfilter():
        selecionados = {id_input: getattr(input, id_input)() for id_input, _, _ in filtros}
        for id_input, coluna, placeholder in filtros:
            subconjunto = df
            for outro_id, outra_coluna, _ in filtros:
                if outro_id == id_input:
                    continue
                valor = selecionados[outro_id]
                if valor:
                    subconjunto = subconjunto[subconjunto[outra_coluna] == valor]
            validos = sorted(v for v in subconjunto[coluna].dropna().unique() if v != "")
            atual = selecionados[id_input]
            ui.update_selectize(
                id_input,
                choices=escolhas_filtro(validos, placeholder),
                selected=atual if atual in validos else "",
            )


def estilo_moeda(df, *colunas: str) -> list[dict]:
    """Alinha à direita e deixa em negrito as colunas de valor monetário
    (R$) de uma tabela `render.DataGrid`, no mesmo padrão do site estático
    (onde a última coluna — ou as duas últimas, na Regionalização — de
    valor numérico é alinhada à direita).
    """
    indices = [df.columns.get_loc(c) for c in colunas if c in df.columns]
    if not indices:
        return []
    return [{"cols": indices, "style": {"text-align": "right", "font-weight": "600"}}]


def botoes_exportar(id_csv: str, id_xlsx: str) -> ui.Tag:
    return ui.div(
        ui.download_button(id_csv, "Exportar CSV", class_="botao-exportar"),
        ui.download_button(id_xlsx, "Exportar Excel", class_="botao-exportar"),
        class_="tabela-exportar",
    )


def botao_limpar_filtros(id: str) -> ui.Tag:
    """Botão "Limpar filtros" com o mesmo visual do site estático/Observable
    (`.botao-secundario`): borda sutil, fundo branco, texto em negrito.
    """
    return ui.input_action_button(id, "Limpar filtros", class_="botao-limpar-filtros")


def card_kpi(
    titulo: str, valor: str, icone: str | None = "coins", compacto: bool = False
) -> ui.Tag:
    """Card de KPI usando o value_box nativo do Shiny (sombra, cor de marca e
    ícone opcional — mais polido que uma div plana), ainda com as classes
    `valor`/`titulo` para os testes e para quem quiser reaproveitar o CSS.

    `compacto=True` reduz a altura vertical do card (usado na Visão Geral).
    """
    classes = "card-kpi" + (" card-kpi--compacto" if compacto else "")
    return ui.value_box(
        ui.span(titulo, class_="titulo"),
        ui.span(valor, class_="valor"),
        showcase=faicons.icon_svg(icone) if icone else None,
        showcase_layout="left center",
        theme=_TEMA_CARD,
        class_=classes,
        full_screen=False,
    )
