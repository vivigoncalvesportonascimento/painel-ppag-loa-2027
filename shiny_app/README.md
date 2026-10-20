# Painel PPAG-LOA 2027 — versão Shiny for Python + Shinylive

Mesmo painel do site estático (`../site_estatico/`) e da versão Observable
Framework (`../observable/`), reconstruído com [Shiny for
Python](https://shiny.posit.co/py/) + [Shinylive](https://shiny.posit.co/py/docs/shinylive.html)
para comparação entre ferramentas. Mesmos dados, mesmas regras de negócio
(ver `../docs/premissas.md`), mesmos filtros/exportações — só muda a
ferramenta. Roda inteiramente no navegador (Python compilado para
WebAssembly via Pyodide), sem servidor — por isso pode ser publicado como
site estático comum.

## Arquitetura

- `app.py`: monta o `page_navbar` com as 12 páginas e registra o server de
  cada uma.
- `paginas/*.py`: uma página por arquivo, cada uma com `panel_ui()` (layout)
  e `register_server(input, output, session)` (reatividade).
- `dados_app.py`: carrega os CSVs pré-processados uma única vez.
- `componentes.py`, `graficos.py`, `utils.py`, `exportar.py`: helpers
  reaproveitados entre páginas (cards `value_box`, gráficos Plotly,
  formatação, exportação CSV/Excel com a mesma sanitização contra injeção
  de fórmula usada nos outros dois painéis).
- `data/*.csv` + `mg_municipios.geojson`: gerados por
  `../gerar_dados_shiny.py`, que importa diretamente os módulos
  `dados_*.py`/`etl/*.py` da raiz do repositório (mesma lógica e premissas,
  zero duplicação de regra de negócio). Pré-processar os dados assim (em
  vez de ler as bases .xlsx/.txt brutas dentro do Pyodide) mantém o app
  leve e rápido para carregar no navegador.
- `www/estilo.css`: identidade visual (cor de marca #0047AB sobreposta via
  variáveis do Bootstrap — ver nota sobre `libsass` abaixo).
- `requirements.txt`: pacotes que não são nativos do Pyodide e precisam ser
  buscados do PyPI (hoje só `openpyxl`, usado na exportação Excel).

## Rodar localmente

Pré-requisito: ambiente Poetry da raiz do repositório instalado
(`poetry install`, a partir da raiz).

```sh
# a partir da raiz do repositorio
poetry run python gerar_dados_shiny.py      # gera/atualiza shiny_app/data
poetry run shiny run shiny_app/app.py       # servidor local (Python nativo, rápido para depurar)
poetry run shinylive export shiny_app dist_shiny   # exporta a versão estática/Pyodide
python -m http.server --directory dist_shiny --bind localhost 8008
```

**Nota sobre tema:** `app.py` não passa um `ui.Theme(...)` customizado —
qualquer `Theme` dispara compilação SASS via `libsass`, que não está
disponível no Pyodide. A cor de marca é aplicada via variáveis CSS do
Bootstrap (`--bs-primary` etc.) em `www/estilo.css` em cima do preset
"shiny" padrão (CSS pré-compilado, sem precisar compilar nada em tempo de
execução).

## Publicar

O `dist_shiny/` gerado é copiado para a branch `gh-pages`, na pasta
`shiny/` (sem mexer na raiz nem em `/observable/`):

```sh
poetry run shinylive export shiny_app dist_shiny
# copiar o conteudo de dist_shiny/ para gh-pages:/shiny/, commitar, dar push
```

Publicado em:
https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/shiny/
