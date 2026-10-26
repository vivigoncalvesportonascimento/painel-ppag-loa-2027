# Painel Shiny Acessível Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a third version of the PPAG-LOA 2027 panel (`shiny_app_acessivel/`, published to `gh-pages:/shiny-acessivel/`) that reuses 100% of the existing Shiny panel's reactive logic and data, with a redesigned sidebar-nav visual layer and new accessibility features (accessible table toggle per chart, visible focus states, skip link).

**Architecture:** Duplicate `shiny_app/` wholesale, then touch only the presentation layer: swap `page_navbar` for a sidebar (`navset_pill_list`), rewrite `www/estilo.css` with new tokens/typography, add a `grafico_acessivel()` helper in `componentes.py` that wraps every `plotly_html()` chart with a "Ver como tabela" toggle, and restyle `card_kpi()`. No page's `@reactive.calc`/`@render.*` logic changes — only what each page's `panel_ui()`/chart-rendering calls build.

**Tech Stack:** Shiny for Python + Shinylive (same as `shiny_app/`), Plotly (embedded HTML, no shinywidgets), pandas, Playwright for verification (no persisted pytest suite in this repo — Playwright scripts are run ad hoc per task, matching the project's established pattern).

**Spec:** `docs/superpowers/specs/2026-10-26-painel-shiny-acessivel-design.md`

## Global Constraints

- New code only in `shiny_app_acessivel/` (on `main`) and `/shiny-acessivel/` (on `gh-pages`). Never modify `shiny_app/`, `site_estatico/`, the published `/shiny/`, or the root `dados_*.py`/`etl/*.py` modules.
- No change to any page's reactive logic (filters, crossfilter, gating, exports, resizable columns, the map). Only `panel_ui()` markup and shared `componentes.py` helpers change.
- No new content or reorganized information architecture — same 12 pages, same data, same filters.
- Typography: "Lexend" (headings) + "Public Sans" (body) via a Google Fonts `<link>`, same CDN-script pattern already used for Plotly.js.
- No `ui.Theme(...)` — it triggers SASS compilation via `libsass`, unavailable in Pyodide. Keep overriding Bootstrap CSS variables directly, as `shiny_app/www/estilo.css` already does.
- `requirements.txt` (listing `openpyxl`) is copied as-is — without it, Excel export fails silently under Shinylive.
- Every chart wrapped by the new `grafico_acessivel()` helper must give its embedded Plotly `<div>` an id distinct from the `@render.ui` output wrapper's id (the `__plot` suffix convention `plotly_html()` already uses) — an id collision breaks rendering silently, no console error.
- Before every push to `gh-pages`, confirm with `git diff --cached --stat` that only `/shiny-acessivel/` is touched.
- This project's shell (Windows + git-bash) does not reliably keep a `shiny run ... &` background process alive across separate tool calls. Every task's steps below show `shiny run app.py --port 8124 &` for readability, but start it with whatever backgrounding mechanism your own tools actually persist across calls (e.g. a `run_in_background` Bash option, or PowerShell's `Start-Process -RedirectStandardOutput ... -WindowStyle Hidden`) — confirmed working in this exact repo earlier in this project. Always `curl` or `Invoke-WebRequest` the port after starting it and before running a Playwright script against it, and always stop the process at the end of the task (port 8124 for native dev, port 8009 in Task 10 for the WASM build) so the next task's `shiny run` doesn't collide with a leftover process on the same port.

## Review Focus

- A chart wrapped by `grafico_acessivel()` whose "Ver como tabela" button is clicked: the accessible `<table>` must reflect the chart's *current* reactive data (after any filter/crossfilter selection), not a stale snapshot from first render — covered in Task 3's step verifying the table updates after a filter change.
- Clicking a bar on a chart now wrapped by `grafico_acessivel()` must still fire the existing crossfilter (`<id>_selecionado` input) exactly as before — covered in Tasks 4-7's crossfilter regression steps.
- A keyboard-only user pressing Tab then Enter on the skip link must land focus inside the main content region, not just scroll the page visually — covered in Task 2's skip-link step.
- The sidebar nav must usably stack above the content (full width, no squeezed column) at phone width (~390px), since `navset_pill_list`'s default Bootstrap column split has never been exercised at that width in this codebase — covered in Task 2's responsive step.
- A page with no chart (Programa, QDD, LOA Investimentos, Regionalização's table, Glossário, Links Úteis, Sobre) must inherit the new palette/typography purely from the shared CSS/componentes.py changes, with zero `paginas/*.py` edits — covered in Task 9's full-site pass, which asserts these pages' Python files are byte-identical to `shiny_app/`'s.

---

### Task 1: Scaffold `shiny_app_acessivel/` as a verified copy

**Files:**
- Create: `shiny_app_acessivel/` (full copy of `shiny_app/`)

**Interfaces:**
- Produces: a working, unmodified duplicate app, served on port 8124 (distinct from `shiny_app/`'s usual 8123) for the rest of this plan to build on.

- [ ] **Step 1: Copy the directory tree**

```bash
cd /c/projects/painel-ppag-loa-2027
cp -r shiny_app shiny_app_acessivel
find shiny_app_acessivel -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
rm -f shiny_app_acessivel/shiny_out.log shiny_app_acessivel/shiny_err.log
```

- [ ] **Step 2: Run the copy natively and confirm it serves**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8124/
```
Expected: `200`

- [ ] **Step 3: Write and run the baseline parity check**

```python
# scratchpad/_check_baseline.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".navbar-nav", timeout=15000)
    pg.wait_for_timeout(1000)
    abas = pg.locator(".navbar-nav a.nav-link").all_inner_texts()
    assert len(abas) == 12, f"esperava 12 abas, achei {len(abas)}: {abas}"
    print("abas:", abas)
    print("OK: copia identica ao original antes de qualquer mudanca visual")
    b.close()
```

Run: `python scratchpad/_check_baseline.py`
Expected: prints the same 12 tab names as `shiny_app/`, no assertion error (this is the pre-change baseline — the navbar still looks exactly like the original at this point, since nothing has been edited yet).

- [ ] **Step 4: Stop the server and commit**

```bash
kill %1 2>/dev/null || true
cd /c/projects/painel-ppag-loa-2027
git add shiny_app_acessivel
git commit -m "Scaffold shiny_app_acessivel/ as a verified copy of shiny_app/"
```

---

### Task 2: App shell — sidebar navigation, skip link, typography foundation

**Files:**
- Modify: `shiny_app_acessivel/app.py`
- Modify: `shiny_app_acessivel/www/estilo.css`

**Interfaces:**
- Consumes: `pagina.panel_ui()` from each of the 12 page modules — unchanged signature, still returns `ui.nav_panel(...)`.
- Produces: `id="conteudo-principal"` landmark div (skip-link target), `.app-cabecalho`/`.app-conteudo`/`.skip-link` CSS classes other tasks can rely on existing.

- [ ] **Step 1: Rewrite `app.py`'s `app_ui`**

Replace the `page_navbar`-based `app_ui` with a `page_bootstrap` + `navset_pill_list` shell (`page_bootstrap` keeps normal document scrolling, unlike `page_fillable`, matching the original's behavior):

```python
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
```

- [ ] **Step 2: Add the sidebar/typography/skip-link/focus tokens to `estilo.css`**

Add at the very top of `shiny_app_acessivel/www/estilo.css`, before the existing `:root` block (keep every existing rule below as-is for now — later tasks restyle specific components):

```css
/* Fundação visual da versão acessível: tipografia, menu lateral, skip
link e foco visível. As variáveis de cor/sombra já existentes no
:root abaixo continuam valendo para o que ainda não foi redesenhado. */
:root {
  --fonte-titulo: "Lexend", system-ui, sans-serif;
  --fonte-corpo: "Public Sans", system-ui, sans-serif;
  --cor-apoio: #0e7a5c;
  --cor-apoio-escuro: #0b2e26;
}

body {
  font-family: var(--fonte-corpo);
}

h1, h2, h3, h4, h5, h6, .titulo-pagina {
  font-family: var(--fonte-titulo);
}

/* Skip link: fora da tela até receber foco por teclado. */
.skip-link {
  position: absolute;
  left: -999px;
  top: 0;
  background: var(--cor-marca);
  color: #fff;
  padding: 10px 18px;
  border-radius: 0 0 8px 0;
  font-weight: 600;
  z-index: 1000;
}

.skip-link:focus {
  left: 0;
}

/* Foco visível consistente em todo elemento interativo. */
a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
.nav-link:focus-visible,
[tabindex]:focus-visible {
  outline: 3px solid var(--cor-apoio);
  outline-offset: 2px;
}

.app-cabecalho {
  background: #ffffff;
  border-bottom: 1px solid var(--cor-borda);
  padding: 14px 20px;
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.app-titulo {
  font-family: var(--fonte-titulo);
  font-weight: 700;
  font-size: 1.3rem;
  color: var(--cor-marca);
}

.app-subtitulo {
  font-family: var(--fonte-corpo);
  font-size: 0.85rem;
  color: var(--cor-texto-suave);
}

.app-conteudo {
  padding: 18px 20px;
}

/* navset_pill_list gera uma .row com duas colunas Bootstrap: a 1a
(largura "widths[0]") e a 2a (largura "widths[1]"). Estiliza a coluna
da navegação como menu lateral fixo, verde institucional. */
.app-conteudo > .row > div:first-child {
  background: var(--cor-apoio-escuro);
  border-radius: 10px;
  padding: 14px 10px;
}

.app-conteudo .nav-pills {
  flex-direction: column;
  gap: 2px;
}

.app-conteudo .nav-pills .nav-link {
  color: #cfe3dc;
  font-weight: 600;
  font-size: 0.85rem;
  border-radius: 7px;
  padding: 9px 12px;
  text-align: left;
}

.app-conteudo .nav-pills .nav-link.active {
  background: #143d33;
  color: #ffffff;
}

/* Abaixo de ~760px o menu lateral empilha acima do conteudo em vez de
ficar espremido ao lado (largura total, nao mais em coluna estreita). */
@media (max-width: 760px) {
  .app-conteudo > .row > div:first-child {
    margin-bottom: 14px;
  }
  .app-conteudo .nav-pills {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
```

- [ ] **Step 3: Run the app and verify the shell renders**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
```

```python
# scratchpad/_check_shell.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.wait_for_timeout(1000)

    itens = pg.locator(".nav-pills .nav-link").all_inner_texts()
    assert len(itens) == 12, f"esperava 12 itens no menu, achei {len(itens)}: {itens}"

    pg.locator(".nav-pills .nav-link", has_text="Visão Geral").first.click()
    pg.wait_for_timeout(600)
    assert "Visão Geral" in pg.locator(".tab-pane.active").inner_text()

    titulo = pg.locator(".app-titulo").inner_text()
    assert titulo == "Painel PPAG-LOA 2027"

    print("OK: menu lateral com 12 itens, navegacao funciona, cabecalho presente")
    b.close()
```

Run: `python scratchpad/_check_shell.py`
Expected: prints the OK line, no assertion error.

- [ ] **Step 4: Verify the skip link moves keyboard focus**

```python
# scratchpad/_check_skiplink.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.wait_for_timeout(500)

    pg.keyboard.press("Tab")  # primeiro elemento focavel da pagina = skip link
    foco = pg.evaluate("document.activeElement.textContent")
    assert foco.strip() == "Pular para o conteúdo", f"foco inesperado: {foco!r}"

    pg.keyboard.press("Enter")
    pg.wait_for_timeout(300)
    id_focado = pg.evaluate("document.activeElement.id")
    assert id_focado == "conteudo-principal", f"skip link nao moveu o foco, id atual: {id_focado!r}"

    print("OK: skip link move o foco de teclado para #conteudo-principal")
    b.close()
```

Run: `python scratchpad/_check_skiplink.py`
Expected: prints the OK line.

- [ ] **Step 5: Verify the sidebar stacks at phone width**

```python
# scratchpad/_check_mobile_nav.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.wait_for_timeout(600)

    nav_box = pg.locator(".app-conteudo > .row > div").first.bounding_box()
    assert nav_box["width"] > 300, f"menu lateral nao ocupou a largura toda no celular: {nav_box['width']}px"

    overflow = pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    assert not overflow, "pagina com scroll horizontal em largura de celular"

    print("OK: menu empilha em largura total no celular, sem scroll horizontal")
    b.close()
```

Run: `python scratchpad/_check_mobile_nav.py`
Expected: prints the OK line.

- [ ] **Step 6: Stop the server, clean up scratch scripts, commit**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_shell.py scratchpad/_check_skiplink.py scratchpad/_check_mobile_nav.py
cd /c/projects/painel-ppag-loa-2027
git add shiny_app_acessivel/app.py shiny_app_acessivel/www/estilo.css
git commit -m "Add sidebar nav, skip link and typography foundation to shiny_app_acessivel"
```

---

### Task 3: `componentes.py` — accessible chart helper and KPI card redesign, wired into Visão Geral

**Files:**
- Modify: `shiny_app_acessivel/componentes.py`
- Modify: `shiny_app_acessivel/paginas/visao_geral.py`
- Modify: `shiny_app_acessivel/www/estilo.css`

**Interfaces:**
- Produces: `grafico_acessivel(fig, df, id, titulo, selecionavel=False)` — same call shape as `plotly_html(fig, id=..., selecionavel=...)` plus one required `df` (the dataframe the chart was built from), returning a `ui.Tag` with the chart plus a toggle button and a paired `<table>`. Every later task (4-7) consumes this exact signature.
- Consumes: nothing new — builds on the existing `plotly_html()` id-suffix convention (`__plot`).

- [ ] **Step 1: Add `grafico_acessivel()` to `componentes.py`**

Add `import html` to the top of the file, alongside the existing `import faicons`:

```python
import faicons
import html
from shiny import reactive, ui
from shiny.types import SilentException
```

Then add this function after the existing `plotly_html()` function:

```python
def grafico_acessivel(fig, df, id: str, titulo: str, selecionavel: bool = False) -> ui.Tag:
    """Como `plotly_html()`, mas com um botão "Ver como tabela" ao lado
    que alterna a visibilidade entre o gráfico e uma <table> semântica
    com os mesmos dados de `df` -- para quem usa leitor de tela/teclado,
    ou só quer os números exatos sem passar o mouse sobre as barras.

    A tabela é reconstruída a cada render (como o gráfico), então
    reflete sempre os dados atuais -- incluindo depois de um filtro ou
    de uma seleção de crossfilter.
    """
    id_tabela = f"{id}__tabela"
    linhas_html = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(valor))}</td>" for valor in linha) + "</tr>"
        for linha in df.itertuples(index=False)
    )
    cabecalho_html = "".join(f'<th scope="col">{html.escape(str(coluna))}</th>' for coluna in df.columns)
    titulo_escapado = html.escape(titulo)

    return ui.div(
        ui.tags.button(
            "Ver como tabela",
            type="button",
            class_="botao-ver-tabela",
            **{
                "aria-expanded": "false",
                "aria-controls": id_tabela,
                "onclick": (
                    f"var t=document.getElementById('{id_tabela}');"
                    f"var oculto=t.hidden; t.hidden=!oculto;"
                    f"this.setAttribute('aria-expanded', String(oculto));"
                    f"this.textContent = oculto ? 'Ver como gráfico' : 'Ver como tabela';"
                ),
            },
        ),
        plotly_html(fig, id=id, selecionavel=selecionavel),
        ui.HTML(
            f'<table id="{id_tabela}" hidden class="tabela-acessivel" aria-label="{titulo_escapado}">'
            f"<thead><tr>{cabecalho_html}</tr></thead>"
            f"<tbody>{linhas_html}</tbody>"
            f"</table>"
        ),
        class_="grafico-acessivel",
    )
```

- [ ] **Step 2: Redesign `card_kpi()` to match the approved mockup**

Replace the existing `card_kpi()` function body:

```python
def card_kpi(
    titulo: str, valor: str, icone: str | None = "coins", compacto: bool = False
) -> ui.Tag:
    """Card de KPI com borda de destaque à esquerda (verde institucional)
    e número grande, no padrão aprovado na maquete "Painel Lateral" --
    sem o fundo azul sólido da versão original, para melhor contraste em
    qualquer combinação de cores dentro do card.
    """
    classes = "card-kpi" + (" card-kpi--compacto" if compacto else "")
    return ui.div(
        ui.span(valor, class_="valor"),
        ui.span(titulo, class_="titulo"),
        class_=classes,
    )
```

(This drops the `faicons`/`value_box` dependency for the KPI card entirely — the approved mockup's KPI tiles have no icon, just a left accent border and a large number. The `icone`/`compacto` parameters stay for call-site compatibility with the 7 existing `card_kpi(...)` call sites across `paginas/*.py`, even though `icone` is now unused; removing the parameter would require touching every call site for no behavioral gain.)

- [ ] **Step 3: Add the new CSS classes**

Append to `shiny_app_acessivel/www/estilo.css`:

```css
/* Card de KPI: borda verde a esquerda, numero grande (maquete B). */
.card-kpi {
  background: #ffffff;
  border: 1px solid var(--cor-borda);
  border-left: 4px solid var(--cor-apoio);
  border-radius: 8px;
  padding: 12px 14px;
  box-shadow: var(--sombra-card);
}

.card-kpi .valor {
  display: block;
  font-family: var(--fonte-titulo);
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--cor-apoio-escuro);
  line-height: 1.2;
}

.card-kpi .titulo {
  display: block;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--cor-texto-suave);
  margin-top: 2px;
}

.card-kpi--compacto {
  padding: 10px 12px;
}

.card-kpi--compacto .valor {
  font-size: 1.05rem;
}

/* Grafico + toggle "Ver como tabela" */
.grafico-acessivel {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.botao-ver-tabela {
  align-self: flex-end;
  appearance: none;
  border: 1px solid var(--cor-borda);
  border-radius: 6px;
  background: #ffffff;
  color: var(--cor-apoio-escuro);
  padding: 5px 10px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.botao-ver-tabela:hover {
  background: #eef6f3;
  border-color: var(--cor-apoio);
}

.tabela-acessivel {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.tabela-acessivel th,
.tabela-acessivel td {
  border: 1px solid var(--cor-borda);
  padding: 6px 10px;
  text-align: left;
}

.tabela-acessivel th {
  background: #f3f7f5;
  font-weight: 600;
}
```

- [ ] **Step 4: Wire `grafico_acessivel()` into Visão Geral (first consumer)**

In `shiny_app_acessivel/paginas/visao_geral.py`, the current chart renderers are:

```python
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
```

Change the import and both renderers:

```python
from componentes import botao_limpar_filtros, card_kpi, grafico_acessivel, limpar_selecao_graficos, selecao_grafico
```

```python
    @render.ui
    def vg_grafico_area():
        df = _base_para_area()
        fig = grafico_percentual_horizontal(
            df, "area_tematica", "valor", "Previsão 2027 por Área Temática"
        )
        tabela = df.groupby("area_tematica", as_index=False)["valor"].sum().rename(
            columns={"area_tematica": "Área Temática", "valor": "Valor (R$)"}
        )
        return grafico_acessivel(
            fig, tabela, id="vg_grafico_area", titulo="Previsão 2027 por Área Temática", selecionavel=True
        )

    @render.ui
    def vg_grafico_setor():
        df = _base_para_setor()
        fig = grafico_percentual_horizontal(
            df, "setor_governo", "valor", "Previsão 2027 por Setor de Governo"
        )
        tabela = df.groupby("setor_governo", as_index=False)["valor"].sum().rename(
            columns={"setor_governo": "Setor de Governo", "valor": "Valor (R$)"}
        )
        return grafico_acessivel(
            fig, tabela, id="vg_grafico_setor", titulo="Previsão 2027 por Setor de Governo", selecionavel=True
        )
```

- [ ] **Step 5: Verify Visão Geral's charts, toggle, and crossfilter**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
```

```python
# scratchpad/_check_visao_geral.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.locator(".nav-pills .nav-link", has_text="Visão Geral").first.click()
    pg.wait_for_timeout(1200)

    ativa = pg.locator(".tab-pane.active")
    assert ativa.locator("#vg_grafico_area__plot svg").count() > 0, "grafico de area nao renderizou"

    # KPI card: layout novo (sem fundo azul solido, com classe valor/titulo)
    primeiro_card = ativa.locator(".card-kpi").first
    assert primeiro_card.locator(".valor").count() == 1

    # toggle "ver como tabela"
    botao = ativa.locator("#vg_grafico_area__plot").locator("xpath=../..").locator(".botao-ver-tabela")
    tabela = ativa.locator("#vg_grafico_area__tabela")
    assert tabela.is_hidden()
    botao.click()
    pg.wait_for_timeout(200)
    assert tabela.is_visible(), "tabela nao apareceu ao clicar em Ver como tabela"
    linhas_antes = tabela.locator("tbody tr").count()
    assert linhas_antes > 0

    # crossfilter ainda funciona depois do wrap em grafico_acessivel
    n_antes = ativa.locator("#vg_grafico_area__plot .points .point path").count()
    ativa.locator("#vg_grafico_setor__plot .points .point path").first.click(force=True)
    pg.wait_for_timeout(700)
    n_depois = ativa.locator("#vg_grafico_area__plot .points .point path").count()
    assert n_depois < n_antes, "crossfilter parou de funcionar apos o wrap em grafico_acessivel"

    # a tabela acompanha a nova selecao (nao fica com os dados antigos)
    linhas_depois = pg.locator("#vg_grafico_area__tabela tbody tr").count()
    assert linhas_depois != linhas_antes or linhas_depois == 1, (
        "tabela acessivel nao atualizou junto com o grafico filtrado"
    )

    print("OK: Visao Geral com card novo, toggle ver-como-tabela e crossfilter intactos")
    b.close()
```

Run: `python scratchpad/_check_visao_geral.py`
Expected: prints the OK line. (If the `aria-expanded` xpath lookup is brittle in practice, replace it with `ativa.locator(".botao-ver-tabela").first` — there is exactly one such button on this page at this point in the plan.)

- [ ] **Step 6: Stop the server, clean up, commit**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_baseline.py scratchpad/_check_visao_geral.py
cd /c/projects/painel-ppag-loa-2027
git add shiny_app_acessivel/componentes.py shiny_app_acessivel/paginas/visao_geral.py shiny_app_acessivel/www/estilo.css
git commit -m "Add grafico_acessivel() and redesigned card_kpi(), wired into Visao Geral"
```

---

### Task 4: Ação Orçamentária — retrofit both charts

**Files:**
- Modify: `shiny_app_acessivel/paginas/acao_orcamentaria.py`

**Interfaces:**
- Consumes: `grafico_acessivel(fig, df, id, titulo, selecionavel=False)` from Task 3.

- [ ] **Step 1: Swap both `plotly_html(...)` calls**

In the `ac_conteudo()` render function, the current code builds two figures:

```python
        valores_fisica = [float(linha[f"fisica_{ano}"]) for ano in _ANOS]
        fig_fisica = grafico_por_ano(
            _ANOS, valores_fisica, "Previsão Física", lambda v: f"{v:,.0f}".replace(",", ".")
        )
        valores_orcamentaria = [float(linha[f"orcamentaria_{ano}"]) for ano in _ANOS]
        fig_orcamentaria = grafico_por_ano(_ANOS, valores_orcamentaria, "Previsão Orçamentária", formatar_moeda)
```
```python
            ui.div(
                ui.div(plotly_html(fig_fisica), class_="grafico-card"),
                ui.div(plotly_html(fig_orcamentaria), class_="grafico-card"),
                class_="grade-graficos",
            ),
```

Replace the import line (`plotly_html` becomes unused on this page — both its call sites become `grafico_acessivel`):

```python
from componentes import botao_limpar_filtros, filtro_selectize, grafico_acessivel, registrar_filtros_cruzados
```

Then replace the two `plotly_html(...)` calls:

```python
        tabela_fisica = pd.DataFrame({"Ano": _ANOS, "Previsão Física": valores_fisica})
        tabela_orcamentaria = pd.DataFrame(
            {"Ano": _ANOS, "Previsão Orçamentária (R$)": [formatar_moeda(v) for v in valores_orcamentaria]}
        )
```
```python
            ui.div(
                ui.div(
                    grafico_acessivel(fig_fisica, tabela_fisica, id="ac_grafico_fisica", titulo="Previsão Física"),
                    class_="grafico-card",
                ),
                ui.div(
                    grafico_acessivel(
                        fig_orcamentaria, tabela_orcamentaria, id="ac_grafico_orcamentaria", titulo="Previsão Orçamentária"
                    ),
                    class_="grafico-card",
                ),
                class_="grade-graficos",
            ),
```

(Neither chart on this page is `selecionavel` — they display the single currently-gated ação, there is nothing to cross-filter.)

- [ ] **Step 2: Verify the gating rule, both charts, and both toggles**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
```

```python
# scratchpad/_check_acao.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.locator(".nav-pills .nav-link", has_text="Ação Orçamentária").first.click()
    pg.wait_for_timeout(600)
    ativa = pg.locator(".tab-pane.active")

    # gating: mensagem antes de selecionar
    assert "Selecione uma ação orçamentária" in ativa.inner_text()

    ativa.locator("#ac_acao + .selectize-control .selectize-input").click()
    pg.wait_for_timeout(300)
    pg.locator(".selectize-dropdown-content .option:visible").first.click()
    pg.wait_for_timeout(600)

    assert ativa.locator("#ac_grafico_fisica__plot svg").count() > 0
    assert ativa.locator("#ac_grafico_orcamentaria__plot svg").count() > 0

    botoes = ativa.locator(".botao-ver-tabela")
    assert botoes.count() == 2
    botoes.first.click()
    pg.wait_for_timeout(200)
    assert ativa.locator("#ac_grafico_fisica__tabela").is_visible()

    print("OK: Acao Orcamentaria com gating, 2 graficos e 2 toggles funcionando")
    b.close()
```

Run: `python scratchpad/_check_acao.py`
Expected: prints the OK line.

- [ ] **Step 3: Stop the server, clean up, commit**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_acao.py
cd /c/projects/painel-ppag-loa-2027
git add shiny_app_acessivel/paginas/acao_orcamentaria.py
git commit -m "Retrofit Acao Orcamentaria charts with grafico_acessivel"
```

---

### Task 5: Despesa Fiscal — retrofit all 3 charts (3-way crossfilter)

**Files:**
- Modify: `shiny_app_acessivel/paginas/despesa_fiscal.py`

**Interfaces:**
- Consumes: `grafico_acessivel(...)` from Task 3.

- [ ] **Step 1: Swap all 3 `plotly_html(...)` calls**

```python
    @render.ui
    def df_grafico_poder():
        df = base_para_poder()
        fig = grafico_absoluto_vertical(
            df, "uo_poder", "valor", "Despesa por Poder e Reserva de Contingência"
        )
        tabela = df.groupby("uo_poder", as_index=False)["valor"].sum().rename(
            columns={"uo_poder": "Poder", "valor": "Valor (R$)"}
        )
        return grafico_acessivel(
            fig, tabela, id="df_grafico_poder", titulo="Despesa por Poder e Reserva de Contingência", selecionavel=True
        )

    @render.ui
    def df_grafico_grupo():
        df = base_para_grupo()
        fig = grafico_percentual_horizontal(df, "grupo_despesa_descricao", "valor", "Despesa por Grupo")
        tabela = df.groupby("grupo_despesa_descricao", as_index=False)["valor"].sum().rename(
            columns={"grupo_despesa_descricao": "Grupo de Despesa", "valor": "Valor (R$)"}
        )
        return grafico_acessivel(fig, tabela, id="df_grafico_grupo", titulo="Despesa por Grupo", selecionavel=True)

    @render.ui
    def df_grafico_funcao():
        df = base_para_funcao()
        fig = grafico_percentual_horizontal(df, "funcao_descricao", "valor", "Despesa por Função")
        tabela = df.groupby("funcao_descricao", as_index=False)["valor"].sum().rename(
            columns={"funcao_descricao": "Função", "valor": "Valor (R$)"}
        )
        return grafico_acessivel(fig, tabela, id="df_grafico_funcao", titulo="Despesa por Função", selecionavel=True)
```

Replace the import line (`plotly_html` becomes unused — all 3 call sites become `grafico_acessivel`):

```python
from componentes import card_kpi, grafico_acessivel, selecao_grafico
```

- [ ] **Step 2: Verify all 3 charts and the 3-way crossfilter**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
```

```python
# scratchpad/_check_despesa_fiscal.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.locator(".nav-pills .nav-link", has_text="Despesa Fiscal").first.click()
    pg.wait_for_timeout(1000)
    ativa = pg.locator(".tab-pane.active")

    for id_ in ["df_grafico_poder", "df_grafico_grupo", "df_grafico_funcao"]:
        assert ativa.locator(f"#{id_}__plot svg").count() > 0, f"{id_} nao renderizou"

    n_poder_antes = ativa.locator("#df_grafico_poder__plot .points .point path").count()
    ativa.locator("#df_grafico_grupo__plot .points .point path").first.click(force=True)
    pg.wait_for_timeout(700)
    n_poder_depois = ativa.locator("#df_grafico_poder__plot .points .point path").count()
    assert n_poder_depois < n_poder_antes, "crossfilter de 3 vias quebrou apos o wrap"

    assert ativa.locator(".botao-ver-tabela").count() == 3

    print("OK: Despesa Fiscal com 3 graficos e crossfilter de 3 vias intactos")
    b.close()
```

Run: `python scratchpad/_check_despesa_fiscal.py`
Expected: prints the OK line.

- [ ] **Step 3: Stop the server, clean up, commit**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_despesa_fiscal.py
cd /c/projects/painel-ppag-loa-2027
git add shiny_app_acessivel/paginas/despesa_fiscal.py
git commit -m "Retrofit Despesa Fiscal charts with grafico_acessivel"
```

---

### Task 6: Despesa por Órgão — retrofit the chart

**Files:**
- Modify: `shiny_app_acessivel/paginas/despesa_orgao.py`

- [ ] **Step 1: Swap the `plotly_html(...)` call**

```python
    @render.ui
    def do_grafico():
        df = base_filtrada()
        fig = grafico_absoluto_vertical(df, "grupo_despesa_descricao", "valor", "Despesa por Grupo")
        tabela = df.groupby("grupo_despesa_descricao", as_index=False)["valor"].sum().rename(
            columns={"grupo_despesa_descricao": "Grupo de Despesa", "valor": "Valor (R$)"}
        )
        return grafico_acessivel(fig, tabela, id="do_grafico", titulo="Despesa por Grupo", selecionavel=True)
```

Replace the import line (`plotly_html` becomes unused — its one call site becomes `grafico_acessivel`):

```python
from componentes import botao_limpar_filtros, card_kpi, filtro_selectize, grafico_acessivel, selecao_grafico
```

- [ ] **Step 2: Verify the dropdown filter, the chart-click crossfilter, and the toggle**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
```

```python
# scratchpad/_check_despesa_orgao.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.locator(".nav-pills .nav-link", has_text="Despesa por Órgão").first.click()
    pg.wait_for_timeout(1000)
    ativa = pg.locator(".tab-pane.active")

    assert ativa.locator("#do_grafico__plot svg").count() > 0

    valor_antes = ativa.locator(".card-kpi .valor").first.inner_text()
    ativa.locator("#do_grafico__plot .points .point path").first.click(force=True)
    pg.wait_for_timeout(700)
    valor_depois = ativa.locator(".card-kpi .valor").first.inner_text()
    assert valor_antes != valor_depois, "clique no grafico parou de filtrar o card"

    assert ativa.locator(".botao-ver-tabela").count() == 1

    print("OK: Despesa por Orgao com grafico, crossfilter e toggle intactos")
    b.close()
```

Run: `python scratchpad/_check_despesa_orgao.py`
Expected: prints the OK line.

- [ ] **Step 3: Stop the server, clean up, commit**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_despesa_orgao.py
cd /c/projects/painel-ppag-loa-2027
git add shiny_app_acessivel/paginas/despesa_orgao.py
git commit -m "Retrofit Despesa por Orgao chart with grafico_acessivel"
```

---

### Task 7: Receita Fiscal — retrofit the chart (chart + dropdown + "Limpar filtros" interplay)

**Files:**
- Modify: `shiny_app_acessivel/paginas/receita_fiscal.py`

- [ ] **Step 1: Swap the `plotly_html(...)` call**

```python
    @render.ui
    def rf_grafico():
        df = linhas_filtradas()
        fig = grafico_absoluto_horizontal(
            df, "categoria_receita_desc", "valor", "Receitas por Categoria Econômica"
        )
        tabela = df.groupby("categoria_receita_desc", as_index=False)["valor"].sum().rename(
            columns={"categoria_receita_desc": "Categoria Econômica", "valor": "Valor (R$)"}
        )
        return grafico_acessivel(
            fig, tabela, id="rf_grafico", titulo="Receitas por Categoria Econômica", selecionavel=True
        )
```

Replace the import line (`plotly_html` becomes unused — its one call site becomes `grafico_acessivel`):

```python
from componentes import (
    botao_limpar_filtros,
    botoes_exportar,
    card_kpi,
    estilo_moeda,
    filtro_selectize,
    grafico_acessivel,
    limpar_selecao_graficos,
    selecao_grafico,
)
```

- [ ] **Step 2: Verify the chart, crossfilter, and that "Limpar filtros" still clears the chart selection**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
```

```python
# scratchpad/_check_receita_fiscal.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.locator(".nav-pills .nav-link", has_text="Receita Fiscal").first.click()
    pg.wait_for_timeout(1000)
    ativa = pg.locator(".tab-pane.active")

    assert ativa.locator("#rf_grafico__plot svg").count() > 0

    card_antes = ativa.locator(".card-kpi .valor").first.inner_text()
    ativa.locator("#rf_grafico__plot .points .point path").first.click(force=True)
    pg.wait_for_timeout(700)
    card_depois = ativa.locator(".card-kpi .valor").first.inner_text()
    assert card_antes != card_depois, "clique no grafico parou de filtrar o card"

    ativa.get_by_role("button", name="Limpar filtros").click()
    pg.wait_for_timeout(700)
    card_limpo = ativa.locator(".card-kpi .valor").first.inner_text()
    assert card_limpo == card_antes, "Limpar filtros parou de limpar a selecao do grafico"

    print("OK: Receita Fiscal com grafico, crossfilter e Limpar filtros intactos")
    b.close()
```

Run: `python scratchpad/_check_receita_fiscal.py`
Expected: prints the OK line.

- [ ] **Step 3: Stop the server, clean up, commit**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_receita_fiscal.py
cd /c/projects/painel-ppag-loa-2027
git add shiny_app_acessivel/paginas/receita_fiscal.py
git commit -m "Retrofit Receita Fiscal chart with grafico_acessivel"
```

---

### Task 8: Regionalização — visual pass only (map stays plain Plotly)

**Files:**
- Modify: `shiny_app_acessivel/www/estilo.css` (if the map/table need extra rules beyond what Tasks 2-3 already provide)

**Interfaces:**
- Consumes: nothing new. This task makes no Python changes — it only verifies the map, filters, crossfilter, and resizable/right-aligned table columns still work and look right under the inherited CSS, and documents why the map is excluded from the `grafico_acessivel()` toggle.

- [ ] **Step 1: Verify the map, crossfilter, and table inherit the new look correctly**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
```

```python
# scratchpad/_check_regionalizacao.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.locator(".nav-pills .nav-link", has_text="Regionalização").first.click()
    pg.wait_for_timeout(1500)
    ativa = pg.locator(".tab-pane.active")

    assert ativa.locator(".mapa-card svg").count() > 0, "mapa nao renderizou"

    # crossfilter de dropdown (nao e grafico clicavel, e' o crossfilter entre filtros ja existente)
    opcoes_acao_antes = None
    ativa.locator("#rg_uo + .selectize-control .selectize-input").click()
    pg.wait_for_timeout(250)
    opcoes_uo = pg.locator(".selectize-dropdown-content .option:visible").all_inner_texts()
    assert len(opcoes_uo) > 1
    pg.keyboard.press("Escape")

    # tabela redimensionavel e alinhamento a direita (herdados do CSS existente)
    th = ativa.locator(".tabela-card th").first
    largura_antes = th.bounding_box()["width"]
    box = th.bounding_box()
    pg.mouse.move(box["x"] + box["width"] - 2, box["y"] + box["height"] - 2)
    pg.mouse.down()
    pg.mouse.move(box["x"] + box["width"] + 60, box["y"] + box["height"] - 2, steps=8)
    pg.mouse.up()
    pg.wait_for_timeout(200)
    largura_depois = th.bounding_box()["width"]
    assert largura_depois > largura_antes, "coluna da tabela parou de ser redimensionavel"

    print("OK: Regionalizacao com mapa, filtros e tabela redimensionavel intactos")
    b.close()
```

Run: `python scratchpad/_check_regionalizacao.py`
Expected: prints the OK line. If the map or table look visually broken under the new CSS (check by eye, not just this script), add targeted rules to `estilo.css` and re-run.

- [ ] **Step 2: Stop the server, clean up, commit if `estilo.css` changed**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_regionalizacao.py
cd /c/projects/painel-ppag-loa-2027
git add shiny_app_acessivel/www/estilo.css
git status --short  # only commit if something actually changed
git commit -m "Verify Regionalizacao under the new visual layer" \
  -m "No Python changes; map intentionally keeps no accessible-table toggle (the full data table already below it on this page covers that need)." \
  --allow-empty
```

---

### Task 9: Full-site pass — remaining pages, byte-identity check, and cross-page accessibility sweep

**Files:**
- Read-only verification of: `shiny_app_acessivel/paginas/programa.py`, `qdd.py`, `loa_investimentos.py`, `glossario.py`, `links_uteis.py`, `sobre.py`

**Interfaces:**
- Consumes: nothing new. Confirms the Global Constraints promise ("pages with no chart need zero Python edits") held in practice.

- [ ] **Step 1: Confirm the chart-free pages were never touched**

```bash
cd /c/projects/painel-ppag-loa-2027
for f in programa.py qdd.py loa_investimentos.py glossario.py links_uteis.py sobre.py; do
  diff "shiny_app/paginas/$f" "shiny_app_acessivel/paginas/$f" > /dev/null \
    && echo "$f: identico (OK)" \
    || echo "$f: DIFERENTE -- investigar, nao deveria ter mudado"
done
```
Expected: `identico (OK)` for all 6 files. (`sobre.py` legitimately may need one edit — see Step 3 below — in which case this diff is expected to show a difference for that one file only.)

- [ ] **Step 2: Full 12-page smoke test, native**

```bash
cd /c/projects/painel-ppag-loa-2027/shiny_app_acessivel
shiny run app.py --port 8124 &
sleep 7
```

```python
# scratchpad/_check_full_site.py
from playwright.sync_api import sync_playwright

PAGINAS = [
    "Sobre o Painel", "Visão Geral", "Ação Orçamentária", "Programa", "Regionalização",
    "Receita Fiscal", "Despesa Fiscal", "Despesa por Órgão", "QDD", "LOA Investimentos",
    "Glossário", "Links Úteis",
]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    erros = []
    pg.on("pageerror", lambda exc: erros.append(str(exc)))
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)

    for nome in PAGINAS:
        pg.locator(".nav-pills .nav-link", has_text=nome).first.click()
        pg.wait_for_timeout(900)
        ativa = pg.locator(".tab-pane.active")
        assert nome in ativa.inner_text(), f"{nome}: conteudo nao carregou"

    assert not erros, f"erros de JS no console: {erros}"
    print("OK: todas as 12 paginas carregam sem erro de JS")
    b.close()
```

Run: `python scratchpad/_check_full_site.py`
Expected: prints the OK line.

- [ ] **Step 3: Check icon-only controls for `aria-label`**

```python
# scratchpad/_check_aria_labels.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8124/")
    pg.wait_for_selector(".nav-pills", timeout=15000)
    pg.wait_for_timeout(800)

    # Botoes sem texto visivel (apenas icone/simbolo) precisam de aria-label.
    sem_rotulo = pg.evaluate(
        """() => Array.from(document.querySelectorAll('button, a.botao-ver-tabela'))
            .filter(el => el.textContent.trim() === '' && !el.getAttribute('aria-label'))
            .map(el => el.outerHTML.slice(0, 120))"""
    )
    assert sem_rotulo == [], f"controles sem rotulo acessivel encontrados: {sem_rotulo}"

    print("OK: nenhum controle so-icone sem aria-label na pagina inicial")
    b.close()
```

Run: `python scratchpad/_check_aria_labels.py`
Expected: prints the OK line. If it fails, add `aria-label` to whichever control the output names (check each of the 12 pages manually in the browser too, since this check only runs against whatever renders on first load of "Sobre o Painel" — repeat it after navigating to each page that has icon-only controls if any are found).

- [ ] **Step 4: Stop the server, clean up, commit**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_full_site.py scratchpad/_check_aria_labels.py
cd /c/projects/painel-ppag-loa-2027
git add -A shiny_app_acessivel
git status --short
git commit -m "Full-site native verification pass for shiny_app_acessivel" --allow-empty
```

---

### Task 10: Shinylive export and WASM smoke test

**Files:**
- Create (build output, not committed to `main`): `dist_shiny_acessivel/`

- [ ] **Step 1: Export**

```bash
cd /c/projects/painel-ppag-loa-2027
rm -rf dist_shiny_acessivel
shinylive export shiny_app_acessivel dist_shiny_acessivel
```
Expected: `Writing dist_shiny_acessivel\app.json: <N> bytes` with no errors.

- [ ] **Step 2: Serve and re-run the Task 9 full-site check against the WASM build**

```bash
cd /c/projects/painel-ppag-loa-2027
python -m http.server --directory dist_shiny_acessivel --bind 127.0.0.1 8009 &
sleep 3
```

```python
# scratchpad/_check_wasm_full_site.py
import time
from playwright.sync_api import sync_playwright

PAGINAS = [
    "Sobre o Painel", "Visão Geral", "Ação Orçamentária", "Programa", "Regionalização",
    "Receita Fiscal", "Despesa Fiscal", "Despesa por Órgão", "QDD", "LOA Investimentos",
    "Glossário", "Links Úteis",
]


def get_app_frame(page):
    for f in page.frames:
        if "app_" in f.url:
            return f
    return None


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto("http://127.0.0.1:8009/")

    frame = None
    t0 = time.time()
    while time.time() - t0 < 60:
        frame = get_app_frame(pg)
        if frame is not None:
            try:
                if frame.locator(".nav-pills").count() > 0:
                    break
            except Exception:
                pass
        pg.wait_for_timeout(500)
    assert frame is not None, "iframe do app nao encontrado em 60s"
    frame.wait_for_selector(".nav-pills", timeout=30000)
    print(f"app pronto apos {time.time()-t0:.1f}s")

    for nome in PAGINAS:
        frame.locator(".nav-pills .nav-link", has_text=nome).first.click()
        frame.wait_for_timeout(1000)
        assert nome in frame.locator(".tab-pane.active").inner_text(), f"{nome}: nao carregou no WASM"

    # Excel export (pegadinha conhecida: openpyxl precisa estar em requirements.txt)
    frame.locator(".nav-pills .nav-link", has_text="LOA Investimentos").first.click()
    frame.wait_for_timeout(1000)
    with frame.page.expect_download() as download_info:
        frame.get_by_role("link", name="Exportar Excel").click()
    download = download_info.value
    caminho = download.path()
    import os
    assert os.path.getsize(caminho) > 1000, "exportacao Excel falhou silenciosamente (openpyxl ausente?)"

    print("OK: todas as 12 paginas e a exportacao Excel funcionam no build WASM real")
    b.close()
```

Run: `python scratchpad/_check_wasm_full_site.py`
Expected: prints both OK lines.

- [ ] **Step 3: Stop the server, clean up**

```bash
kill %1 2>/dev/null || true
rm -f scratchpad/_check_wasm_full_site.py
rm -rf dist_shiny_acessivel/__pycache__ 2>/dev/null || true
```

(No commit here — `dist_shiny_acessivel/` is a build artifact, gitignored the same way `dist_shiny/` already is; add `dist_shiny_acessivel/` to `.gitignore` alongside the existing `dist_shiny/` entry if not already covered by a wildcard.)

---

### Task 11: Publish to `gh-pages:/shiny-acessivel/`

**Files:**
- Create on `gh-pages`: `/shiny-acessivel/` (full copy of `dist_shiny_acessivel/`)
- Modify: `.gitignore` (add `dist_shiny_acessivel/` if Task 10 didn't already)

- [ ] **Step 1: Commit any remaining `main` changes (e.g. `.gitignore`)**

```bash
cd /c/projects/painel-ppag-loa-2027
git status --short
git add .gitignore  # only if changed
git commit -m "Ignore dist_shiny_acessivel build output" || true
git push origin main
```

- [ ] **Step 2: Re-export fresh (in case any main commit landed after the last export) and stash the in-progress file**

```bash
cd /c/projects/painel-ppag-loa-2027
rm -rf dist_shiny_acessivel
shinylive export shiny_app_acessivel dist_shiny_acessivel
git status --short
git stash push -- prompt_informacoes_elaboracao_painel.txt  # only if it shows modified
```

- [ ] **Step 3: Check out `gh-pages`, confirm it's in sync with the remote**

```bash
cd /c/projects/painel-ppag-loa-2027
git fetch origin gh-pages
git log --oneline -1 origin/gh-pages
git log --oneline -1 gh-pages
git checkout gh-pages
```
Expected: both log lines show the same commit hash before proceeding.

- [ ] **Step 4: Copy the build into `/shiny-acessivel/` and stage only that path**

```bash
cd /c/projects/painel-ppag-loa-2027
mkdir -p shiny-acessivel
cp -r dist_shiny_acessivel/* shiny-acessivel/
git add shiny-acessivel
git status --short
```
Expected: `git status --short` shows only `shiny-acessivel/...` entries as new/modified — no changes to `/`, `/shiny/`, `/observable/` or anything else.

- [ ] **Step 5: Commit and push**

```bash
cd /c/projects/painel-ppag-loa-2027
git commit -m "Publish shiny_app_acessivel to /shiny-acessivel/"
git push origin gh-pages
```

- [ ] **Step 6: Return to `main`, restore the stashed file**

```bash
cd /c/projects/painel-ppag-loa-2027
git checkout main
git stash pop || true
git status --short
```
Expected: only `prompt_informacoes_elaboracao_painel.txt` shows modified (the user's own in-progress file, untouched by this plan).

- [ ] **Step 7: Verify live**

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/shiny-acessivel/
curl -s -o /dev/null -w "%{http_code}\n" https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/shiny/
curl -s -o /dev/null -w "%{http_code}\n" https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/
```
Expected: `200` for all three (the new path is live, and the other two are unaffected).
