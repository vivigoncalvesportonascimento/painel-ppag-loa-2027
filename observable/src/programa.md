---
toc: false
---

# Programa

```js
import { filtroPesquisavel, linhaFiltros } from "./components/filtroPesquisavel.js";
import { acaoCard, gradeAcao } from "./components/detalhe.js";
import { tabela } from "./components/tabela.js";

const dados = await FileAttachment("data/dados.json").json();
const { programas, indicadores } = dados.programa;

const uos = [...new Set(programas.map((p) => p.uo))].sort();
const nomesProgramas = [...new Set(programas.map((p) => p.programa))].sort();

const selectUo = filtroPesquisavel(uos, { label: "Unidade Orçamentária", placeholder: "Selecione..." });
const selectPrograma = filtroPesquisavel(nomesProgramas, { label: "Programa", placeholder: "Selecione..." });
const filtros = linhaFiltros([selectUo, selectPrograma]);
```

${filtros}

```js
const valoresFiltro = Generators.input(filtros);
```

```js
const uoSelecionada = valoresFiltro[0];
const programaSelecionado = valoresFiltro[1];
```

```js
let filtrados = programas;
if (uoSelecionada) filtrados = filtrados.filter((p) => p.uo === uoSelecionada);
if (programaSelecionado) filtrados = filtrados.filter((p) => p.programa === programaSelecionado);
if (filtrados.length === 0) filtrados = programas;

const ordenados = [...filtrados].sort((a, b) => a.uo.localeCompare(b.uo) || a.programa.localeCompare(b.programa));
const programa = ordenados[0];
const tabelaIndicadores = indicadores[programa.codigo] || [];
```

${acaoCard("Programa", programa.programa, { destaque: true })}

${gradeAcao([acaoCard("Unidade Orçamentária", programa.uo), acaoCard("Área Temática", programa.area_tematica)], "30-70")}

${gradeAcao([
  acaoCard("Objetivo", programa.objetivo),
  acaoCard("Objetivo de Desenvolvimento Sustentável - ODS", programa.ods)
], "70-30")}

## Indicadores

${tabela(tabelaIndicadores, [
  {chave: "Indicador", rotulo: "Indicador"},
  {chave: "Periodicidade", rotulo: "Periodicidade"},
  {chave: "Unidade de Medida", rotulo: "Unidade de Medida"},
  {chave: "Índice de Referência", rotulo: "Índice de Referência"},
  {chave: "2027", rotulo: "2027"},
  {chave: "2028", rotulo: "2028"},
  {chave: "2029", rotulo: "2029"},
  {chave: "2030", rotulo: "2030"}
], {nomeArquivo: "indicadores_programa", classeExtra: "tabela-programa-indicadores", semResultadoTexto: "Nenhum indicador para este programa."})}
