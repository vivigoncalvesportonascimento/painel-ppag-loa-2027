---
toc: false
---

# Ação Orçamentária

```js
import { filtroPesquisavel, linhaFiltros } from "./components/filtroPesquisavel.js";
import { acaoCard, gradeAcao } from "./components/detalhe.js";
import { graficoPorAno } from "./components/graficos.js";
import { formatarMoeda } from "./components/utils.js";

const dados = await FileAttachment("data/dados.json").json();
const linhas = dados.acao_orcamentaria.linhas;
const ANOS = [2027, 2028, 2029, 2030];

const uos = [...new Set(linhas.map((l) => l.uo))].sort();
const acoes = [...new Set(linhas.map((l) => l.acao))].sort();

const selectUo = filtroPesquisavel(uos, { label: "Unidade Orçamentária", placeholder: "Selecione..." });
const selectAcao = filtroPesquisavel(acoes, { label: "Ação Orçamentária", placeholder: "Selecione..." });
const filtros = linhaFiltros([selectUo, selectAcao]);
```

${filtros}

```js
const valoresFiltro = Generators.input(filtros);
```

```js
const uoSelecionada = valoresFiltro[0];
const acaoSelecionada = valoresFiltro[1];
```

```js
let filtradas = linhas;
if (uoSelecionada) filtradas = filtradas.filter((l) => l.uo === uoSelecionada);
if (acaoSelecionada) filtradas = filtradas.filter((l) => l.acao === acaoSelecionada);
if (filtradas.length === 0) filtradas = linhas;

const ordenadas = [...filtradas].sort((a, b) => a.uo.localeCompare(b.uo) || a.acao.localeCompare(b.acao));
const linha = ordenadas[0];

const fisicaPorAno = ANOS.map((ano) => ({ ano: String(ano), valor: linha[`fisica_${ano}`] }));
const orcamentariaPorAno = ANOS.map((ano) => ({ ano: String(ano), valor: linha[`orcamentaria_${ano}`] }));
```

${acaoCard("Ação Orçamentária", linha.acao, { destaque: true })}

${gradeAcao([acaoCard("Unidade Orçamentária", linha.uo), acaoCard("Programa", linha.programa)], "30-70")}

${gradeAcao([acaoCard("Finalidade da Ação", linha.finalidade), acaoCard("Público-Alvo", linha.publico_alvo)], "70-30")}

${gradeAcao([
  acaoCard("Identificador de Ação Governamental (IAG)", linha.iag),
  acaoCard("Produto", linha.produto),
  acaoCard("Unidade de Medida (Produto)", linha.unidade_medida)
], "3col")}

<div class="linha-cartoes">
  <div class="grafico-card">${graficoPorAno(fisicaPorAno, (v) => Math.round(v).toLocaleString("pt-BR"))}</div>
  <div class="grafico-card">${graficoPorAno(orcamentariaPorAno, formatarMoeda)}</div>
</div>
