---
toc: false
---

# Receita Fiscal

```js
import { filtroPesquisavel, linhaFiltros } from "./components/filtroPesquisavel.js";
import { cardUnico } from "./components/cards.js";
import { graficoAbsolutoHorizontal } from "./components/graficos.js";
import { tabela } from "./components/tabela.js";
import { formatarBi, formatarMoeda } from "./components/utils.js";

const dados = await FileAttachment("data/dados.json").json();
const linhas = dados.receita_fiscal.linhas;

const uos = [...new Set(linhas.map((l) => l.UO))].sort();
const fontes = [...new Set(linhas.map((l) => l.fonte_de_recursos))].sort();

const selectUo = filtroPesquisavel(uos, { label: "UO" });
const selectFonte = filtroPesquisavel(fontes, { label: "Fonte de Recursos" });
const filtros = linhaFiltros([selectUo, selectFonte]);
```

${filtros}

```js
const valoresFiltro = Generators.input(filtros);
```

```js
const uoSelecionada = valoresFiltro[0];
const fonteSelecionada = valoresFiltro[1];
```

```js
const linhasFiltradas = linhas.filter(
  (l) => (!uoSelecionada || l.UO === uoSelecionada) && (!fonteSelecionada || l.fonte_de_recursos === fonteSelecionada)
);
const totalReceita = linhasFiltradas.reduce((soma, l) => soma + l.valor, 0);
```

<div class="linha-card-grafico">
  <div>${cardUnico(formatarBi(totalReceita), "Receita Total (R$) - 2027")}</div>
  <div class="grafico-card">${graficoAbsolutoHorizontal(linhasFiltradas, "categoria_receita_desc", "valor")}</div>
</div>

```js
const totaisUoFonte = new Map();
for (const linha of linhasFiltradas) {
  const chave = `${linha.UO}|||${linha.fonte_de_recursos}`;
  totaisUoFonte.set(chave, (totaisUoFonte.get(chave) || 0) + linha.valor);
}
const tabelaUoFonte = [...totaisUoFonte.entries()]
  .map(([chave, valor]) => {
    const [UO, fonte_de_recursos] = chave.split("|||");
    return { UO, fonte_de_recursos, valor };
  })
  .sort((a, b) => b.valor - a.valor);
```

${tabela(tabelaUoFonte, [
  {chave: "UO", rotulo: "UO"},
  {chave: "fonte_de_recursos", rotulo: "Fonte de Recursos"},
  {chave: "valor", rotulo: "LOA 2027 (R$)", formatar: formatarMoeda}
], {nomeArquivo: "receita_fiscal_uo_fonte"})}
