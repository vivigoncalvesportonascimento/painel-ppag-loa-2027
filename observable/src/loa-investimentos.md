---
toc: false
---

# LOA Investimentos

```js
import { filtroPesquisavel, linhaFiltros } from "./components/filtroPesquisavel.js";
import { cardUnico } from "./components/cards.js";
import { tabela } from "./components/tabela.js";
import { formatarBi, formatarMoeda } from "./components/utils.js";

const dados = await FileAttachment("data/dados.json").json();
const { uo_opcoes: uoOpcoes, linhas_receita: linhasReceita, linhas_despesa: linhasDespesa } = dados.loa_investimentos;

const selectUo = filtroPesquisavel(uoOpcoes, { label: "Unidade Orçamentária" });
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
const receitaFiltrada = linhasReceita.filter((l) => !uoSelecionada || l.uo_label === uoSelecionada);
const despesaFiltrada = linhasDespesa.filter((l) => !uoSelecionada || l.uo_label === uoSelecionada);
const totalReceita = receitaFiltrada.reduce((soma, l) => soma + l.valor, 0);
const totalDespesa = despesaFiltrada.reduce((soma, l) => soma + l.valor, 0);

const totaisTabela = new Map();
for (const linha of despesaFiltrada) {
  const chave = `${linha.uo_sigla}|||${linha.acao_label}`;
  totaisTabela.set(chave, (totaisTabela.get(chave) || 0) + linha.valor);
}
const linhasTabela = [...totaisTabela.entries()]
  .map(([chave, valor]) => {
    const [uo_sigla, acao_label] = chave.split("|||");
    return { uo_sigla, acao_label, valor };
  })
  .sort((a, b) => b.valor - a.valor);
```

<div class="linha-cartoes">
  ${cardUnico(formatarBi(totalReceita), "Receita Total (R$) - 2027")}
  ${cardUnico(formatarBi(totalDespesa), "Despesa Total (R$) - 2027")}
</div>

${tabela(linhasTabela, [
  {chave: "uo_sigla", rotulo: "Unidade Orçamentária"},
  {chave: "acao_label", rotulo: "Ação Orçamentária"},
  {chave: "valor", rotulo: "LOA 2027 (R$)", formatar: formatarMoeda}
], {nomeArquivo: "loa_investimentos", classeExtra: "tabela-investimentos"})}
