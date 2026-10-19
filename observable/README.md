# Painel PPAG-LOA 2027 — versão Observable Framework

Mesmo painel do site estático (`../site_estatico/`), reconstruído com o
[Observable Framework](https://observablehq.com/framework/) para comparação
entre ferramentas. Mesmos dados, mesmas regras de negócio (ver
`../docs/premissas.md`), mesmos filtros/exportações — só muda a ferramenta.

## Arquitetura

- `src/*.md`: uma página por arquivo (12 páginas, mesmas do site estático).
- `src/components/*.js`: componentes reutilizáveis (filtro pesquisável,
  tabela com exportação CSV/Excel, gráficos Observable Plot, cards, mapa).
- `src/data/*.json.py`: **data loaders** Python que importam diretamente os
  módulos `dados_*.py` / `etl/*.py` da raiz do repositório (mesma lógica e
  premissas do site estático, zero duplicação de regra de negócio) e
  imprimem o JSON no stdout. O Framework os executa automaticamente no
  build, cacheando o resultado.
- `src/data/mg_municipios.geojson`: cópia estática de `../assets/`.

## Rodar localmente

Pré-requisitos: Node.js (LTS) e o ambiente Poetry da raiz do repositório já
instalado (`poetry install`, a partir da raiz).

```sh
npm install
npm run dev      # servidor local com live-reload (observable preview)
npm run build    # gera ./dist (site estático final)
```

**Importante:** `observablehq.config.js` aponta `interpreters[".py"]` para o
caminho absoluto do Python do Poetry (`../.venv/Scripts/python.exe`, Windows).
Se o repositório for clonado em outra máquina/caminho, ajuste esse caminho
(ou troque por `python3` se o `pandas`/`openpyxl`/`plotly` do projeto
estiverem num interpretador acessível por esse nome no PATH).

## Publicar

O `dist/` gerado é copiado para a branch `gh-pages`, na pasta `observable/`
(sem mexer na raiz da branch, que continua servindo o site estático em
`https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/`):

```sh
npm run build
# copiar o conteudo de dist/ para gh-pages:/observable/, commitar, dar push
```

Publicado em:
https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/observable/
