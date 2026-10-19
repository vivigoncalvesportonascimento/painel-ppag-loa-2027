---
toc: false
---

# QDD

<p class="subtitulo">Quadro de Detalhamento da Despesa</p>

```js
import { filtroPesquisavel, linhaFiltros } from "./components/filtroPesquisavel.js";
import { tabela } from "./components/tabela.js";
import { formatarMoeda } from "./components/utils.js";

const dadosQdd = await FileAttachment("data/qdd.json").json();
const linhas = dadosQdd.linhas;

const QDD_FILTROS = [
  ["uo_label", "Unidade Orçamentária"],
  ["programa_label", "Programa"],
  ["acao_label", "Ação Orçamentária"],
  ["grupo_label", "Grupo de Despesa"],
  ["iag_label", "IAG"],
  ["fonte_label", "Fonte de Recursos"],
  ["ipu_label", "IPU"],
  ["elemento_label", "Elemento de Despesa"]
];

const selects = QDD_FILTROS.map(([coluna, rotulo]) =>
  filtroPesquisavel([...new Set(linhas.map((l) => l[coluna]))].sort(), { label: rotulo })
);
const filtros = linhaFiltros(selects);
```

${filtros}

```js
const valoresFiltro = Generators.input(filtros);
```

```js
let filtradas = linhas;
QDD_FILTROS.forEach(([coluna], indice) => {
  const valor = valoresFiltro[indice];
  if (valor) filtradas = filtradas.filter((l) => l[coluna] === valor);
});

const totais = new Map();
for (const linha of filtradas) {
  const chave = QDD_FILTROS.map(([coluna]) => linha[coluna]).join("|||");
  totais.set(chave, (totais.get(chave) || 0) + linha.valor);
}
const linhasTabela = [...totais.entries()]
  .map(([chave, valor]) => {
    const partes = chave.split("|||");
    const linha = { valor };
    QDD_FILTROS.forEach(([coluna], indice) => (linha[coluna] = partes[indice]));
    return linha;
  })
  .sort((a, b) => b.valor - a.valor);
```

${tabela(linhasTabela, [
  ...QDD_FILTROS.map(([chave, rotulo]) => ({ chave, rotulo })),
  { chave: "valor", rotulo: "LOA 2027 (R$)", formatar: formatarMoeda }
], { nomeArquivo: "qdd", classeExtra: "tabela-qdd" })}
