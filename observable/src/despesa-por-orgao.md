---
toc: false
---

# Despesa por Órgão

```js
import { filtroPesquisavel, linhaFiltros } from "./components/filtroPesquisavel.js";
import { cardUnico } from "./components/cards.js";
import { graficoAbsolutoVertical } from "./components/graficos.js";
import { listaCartao } from "./components/lista.js";
import { formatarBi, formatarMoeda, agruparEOrdenar, agruparEPercentual } from "./components/utils.js";

const dados = await FileAttachment("data/dados.json").json();
const linhas = dados.despesa_orgao.linhas;

const uos = [...new Set(linhas.map((l) => l.uo_label))].sort();
const selectUo = filtroPesquisavel(uos, { label: "Unidade Orçamentária" });
const filtros = linhaFiltros([selectUo]);
```

${filtros}

```js
const valoresFiltro = Generators.input(filtros);
```

```js
const uoSelecionada = valoresFiltro[0];
```

```js
const linhasFiltradas = linhas.filter((l) => !uoSelecionada || l.uo_label === uoSelecionada);
const totalDespesa = linhasFiltradas.reduce((soma, l) => soma + l.valor, 0);

const listaAcao = agruparEOrdenar(linhasFiltradas, "acao_label").map((item) => ({
  label: item.label,
  valor: formatarMoeda(item.valor)
}));
const listaFonte = agruparEPercentual(linhasFiltradas, "fonte_label")
  .slice()
  .reverse()
  .map((item) => ({ label: item.label, valor: `${item.percentual.toFixed(1)}%` }));
```

<div class="linha-card-grafico">
  <div>${cardUnico(formatarBi(totalDespesa), "Despesa Total (R$) - 2027")}</div>
  <div class="grafico-card">${graficoAbsolutoVertical(linhasFiltradas, "grupo_despesa_descricao", "valor")}</div>
</div>

<div class="linha-cartoes">
  ${listaCartao("Despesa por Ação Orçamentária", listaAcao)}
  ${listaCartao("Despesa por Fonte de Recursos", listaFonte)}
</div>
