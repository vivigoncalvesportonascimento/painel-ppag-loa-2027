# Painel Shiny Acessível — redesign visual do painel Shiny

## Contexto e objetivo

O usuário mantém hoje dois painéis publicados lado a lado para comparação
(site estático em `/` e Shiny for Python + Shinylive em `/shiny/`), ambos
com as mesmas 12 páginas, mesmos dados e mesmas regras de negócio
(`docs/premissas.md`). Ele pediu um **terceiro painel**, construído a
partir do painel Shiny atual, com melhorias visuais, de acessibilidade e
de "profissionalismo" para o cidadão comum — **sem apagar os dois já
existentes** e **sem mudar o conteúdo/estrutura de informação** (mesmas
12 páginas, mesmo mapa, mesmos filtros, mesmas exportações).

Direção visual aprovada pelo usuário (maquete comparativa publicada e
revisada): **"Painel Lateral"** — menu de navegação fixo à esquerda
(em vez da barra horizontal no topo, que hoje precisa rolar para caber
as 12 páginas), paleta com um verde institucional como cor de apoio ao
azul de marca, KPIs com números grandes, tipografia `Lexend` (títulos)
+ `Public Sans` (corpo) no lugar da fonte padrão do Bootstrap.

## Escopo

**Dentro do escopo:**
- Nova árvore de código em `shiny_app_acessivel/` (cópia de
  `shiny_app/`), publicada em `gh-pages:/shiny-acessivel/`.
- Troca da navbar horizontal (`ui.page_navbar`) por um menu lateral fixo
  (`ui.navset_pill_list`), reaproveitando os mesmos `nav_panel(...)` que
  cada página já retorna — **nenhuma mudança na lógica reativa de
  nenhuma página** (filtros, crossfilter, gating, exportação CSV/Excel,
  colunas redimensionáveis, mapa).
- Novo `www/estilo.css`: paleta com contraste revisado (AA no mínimo,
  AAA onde der), tipografia `Lexend`/`Public Sans` via Google Fonts,
  cards de KPI e gráficos redesenhados conforme a maquete aprovada.
- Acessibilidade nova (funcionalidade, não só estilo):
  - Toggle "Ver como tabela" ao lado de cada gráfico Plotly, mostrando
    os mesmos dados em uma `<table>` semântica (`<th scope="col">`).
  - Estado de foco visível e consistente em filtros, abas do menu
    lateral e pontos de gráfico clicáveis (crossfilter).
  - Link "Pular para o conteúdo" (skip link) no topo da página.
  - `aria-label` em todo controle só-ícone.
- Dados: reaproveita a mesma base já gerada por
  `gerar_dados_shiny.py` — copiada para `shiny_app_acessivel/data/`
  (mesmo conteúdo de `shiny_app/data/`, sem nova lógica de ETL).

**Fora do escopo (confirmado com o usuário):**
- Reorganizar a informação, resumir em linguagem mais simples, adicionar
  conteúdo novo (tipo "Orçamento Cidadão") — fica para uma eventual
  fase futura, não faz parte deste redesign.
- Customizar a tela de carregamento do Shinylive (splash enquanto o
  Pyodide inicializa). Investigar é aceitável; **não é um requisito
  desta entrega** — os arquivos de loading são gerados pelo próprio
  `shinylive export` e pode não ser viável customizá-los sem invadir
  arquivo gerado (risco listado abaixo).
- Qualquer mudança nos dois painéis já publicados (`/`, `/shiny/`).

## Arquitetura

### Onde vive

```
shiny_app_acessivel/        # copia de shiny_app/, com a camada visual trocada
  app.py                    # navset_pill_list em vez de page_navbar
  paginas/*.py               # mesma lógica reativa; só panel_ui() dos
                             #   cards/gráficos muda (via componentes.py)
  componentes.py             # novas versões de card_kpi/plotly_html/etc,
                             #   mais o novo grafico_acessivel()
  www/estilo.css              # paleta, tipografia e layout novos
  data/*.csv + geojson        # copia 1:1 de shiny_app/data/
```

`main`: pasta nova, sem tocar em `shiny_app/`, `site_estatico/`, nem nos
módulos `dados_*.py`/`etl/*.py` da raiz (que continuam a fonte única de
regra de negócio, usada pelas 3 ferramentas).

`gh-pages`: nova pasta `/shiny-acessivel/`, irmã de `/shiny/` — nunca
mexe na raiz nem em `/shiny/` (confirmado com `git diff --cached --stat`
antes de cada push, igual ao fluxo já estabelecido).

### Navegação (mudança central)

Hoje:
```python
app_ui = ui.page_navbar(
    *[pagina.panel_ui() for pagina in _PAGINAS],
    title="Painel PPAG-LOA 2027",
    header=..., footer=...,
)
```

Proposto:
```python
app_ui = ui.page_fillable(
    ui.tags.a("Pular para o conteúdo", href="#conteudo-principal", class_="skip-link"),
    cabecalho_app(),  # faixa com o nome do painel, mais estreita que hoje
    ui.navset_pill_list(
        *[pagina.panel_ui() for pagina in _PAGINAS],
        id="pagina_ativa",
        well=False,
        widths=(2, 10),
    ),
    ...
)
```

Confirmado por inspeção do `shiny.ui.navset_pill_list`: aceita
exatamente os mesmos objetos `ui.nav_panel(...)` que `page_navbar` já
usa — cada `paginas/*.py` continua retornando o que já retorna hoje em
`panel_ui()`; só a casca muda. O estilo do menu (verde institucional,
ícone por página, item ativo destacado) vem inteiramente de CSS sobre
o markup Bootstrap que `navset_pill_list` já gera (`.nav-pills`), sem
reescrever a navegação à mão.

Em telas estreitas (celular), o menu lateral empilha acima do conteúdo
(`widths` não é fixo em px, é fração de 12 colunas Bootstrap — já
responsivo por padrão; CSS adicional só para o visual).

### Toggle "Ver como tabela" (novo componente)

Novo helper em `componentes.py`:

```python
def grafico_acessivel(fig, df, id, titulo) -> ui.Tag:
    """Mesma função de plotly_html(), mais um botão 'Ver como tabela'
    que alterna a visibilidade entre o gráfico Plotly e uma <table>
    semântica construída a partir do mesmo `df` (para quem usa leitor
    de tela ou teclado, ou só quer os números exatos sem passar o
    mouse sobre as barras).
    """
```

Implementação: um botão com `aria-expanded`/`aria-controls` que
mostra/esconde (via `el.hidden`, nunca `style.display`) uma `<table>`
gerada com `df.to_html()` adaptado (cabeçalho com `<th scope="col">`,
sem `class`/`id` do pandas). Reaproveitado em todo lugar que hoje chama
`plotly_html(fig, ...)` com um `df` de apoio disponível (todos os casos:
cada gráfico já vem de um `reactive.calc` que tem o dataframe).

### Paleta e tipografia

Tokens definidos no `:root` de `www/estilo.css` (mesma mecânica CSS já
usada hoje, variáveis sobre o tema `bslib` "shiny" padrão — sem
`ui.Theme()`, que dispara SASS/libsass indisponível no Pyodide):

- `--cor-marca`: azul institucional revisado para contraste AA sobre
  branco E sobre fundo escuro do menu lateral.
- `--cor-apoio`: verde institucional (cor de apoio dos KPIs/menu).
- `--fonte-titulo`: "Lexend" (Google Fonts, carregada via `<link>` no
  `header=` do `page_fillable`, mesmo padrão já usado para o Plotly.js
  via CDN).
- `--fonte-corpo`: "Public Sans".

Todo texto sobre fundo colorido (cards de KPI, menu lateral) é
verificado manualmente (cálculo de contraste) antes de fechar a paleta
final durante a implementação.

### Dados

Sem nova lógica de ETL. `gerar_dados_shiny.py` já gera
`shiny_app/data/*.csv` + `mg_municipios.geojson` a partir dos módulos
`dados_*.py`/`etl/*.py` da raiz. O build da nova versão copia esses
mesmos arquivos para `shiny_app_acessivel/data/` (cópia de arquivo, não
duplicação de lógica) — mesmo padrão que já existe entre site estático
e Shiny (cada ferramenta tem sua própria pasta de dados pré-processados,
gerada a partir da mesma fonte).

## Testes

Mesmo fluxo já estabelecido nas sessões anteriores deste projeto:
1. `shiny run shiny_app_acessivel/app.py` (nativo, rápido) + Playwright:
   todas as 12 páginas carregam, filtros/crossfilter/exportação/mapa
   continuam funcionando (regressão — a lógica não muda), menu lateral
   navega corretamente, toggle "Ver como tabela" funciona, foco visível
   ao tabular.
2. `shinylive export shiny_app_acessivel dist_shiny_acessivel` + mesmo
   teste via Playwright apontando pro `<iframe>` (`app_` no `f.url`),
   confirmando que o que funciona nativo também funciona no build WASM
   real (pegadinhas conhecidas: `libsass`/`ui.Theme`, `openpyxl` via
   `requirements.txt`, IDs de `<div>` do Plotly colidindo com o
   `<div>` de saída do `@render.ui`).
3. Checagem de contraste nas cores finais (cálculo manual ou script
   simples) antes de publicar.

## Risco conhecido

Customizar a tela de carregamento do Shinylive (hoje em branco
enquanto o Pyodide inicializa) depende de arquivos gerados pelo próprio
`shinylive export` (`index.html`, `shinylive-sw.js`) — não é claro se
dá para injetar um splash screen sem "invadir" arquivo gerado de um
jeito que quebre no próximo `export`. Tratado como investigação
oportunista durante a implementação, não como requisito de entrega
(ver Escopo).

## Publicação

Mesmo fluxo de sempre: commit em `main` (pasta nova,
`shiny_app_acessivel/`), export via `shinylive export`, cópia do
`dist_*/app.json` (e runtime, se algo mudar) para
`gh-pages:/shiny-acessivel/`, confirmando com `git diff --cached --stat`
que nada fora dessa pasta nova foi tocado antes de cada push.
