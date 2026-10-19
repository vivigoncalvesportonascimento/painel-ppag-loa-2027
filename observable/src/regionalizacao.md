---
toc: false
---

# Regionalização

```js
import { filtroPesquisavel, linhaFiltros } from "./components/filtroPesquisavel.js";
import { decodificarLinhas } from "./components/regionalizacaoDados.js";
import { mapaRegionalizacao } from "./components/mapa.js";
import { tabela } from "./components/tabela.js";
import { formatarInteiro, formatarMoeda } from "./components/utils.js";

const dadosReg = await FileAttachment("data/regionalizacao.json").json();
const geojson = await FileAttachment("data/mg_municipios.geojson").json();
const linhas = decodificarLinhas(dadosReg);

const selectUo = filtroPesquisavel(dadosReg.uo, { label: "Unidade Orçamentária" });
const selectAcao = filtroPesquisavel(dadosReg.acao, { label: "Ação Orçamentária" });
const selectRegiao = filtroPesquisavel(dadosReg.regiao, { label: "Região Geográfica Intermediária" });
const selectMunicipio = filtroPesquisavel(
  dadosReg.municipios.map((m) => m.nome),
  { label: "Município" }
);
const selectProduto = filtroPesquisavel(dadosReg.produto, { label: "Produto" });
const filtros = linhaFiltros([selectUo, selectAcao, selectRegiao, selectMunicipio, selectProduto]);
```

${filtros}

```js
const valoresFiltro = Generators.input(filtros);
```

```js
const uoSelecionada = valoresFiltro[0];
const acaoSelecionada = valoresFiltro[1];
const regiaoSelecionada = valoresFiltro[2];
const municipioSelecionado = valoresFiltro[3];
const produtoSelecionado = valoresFiltro[4];
```

```js
function aplicarFiltros(ignorarMunicipio) {
  return linhas.filter(
    (l) =>
      (!uoSelecionada || l.uo_label === uoSelecionada) &&
      (!acaoSelecionada || l.acao_label === acaoSelecionada) &&
      (!regiaoSelecionada || l.regiao === regiaoSelecionada) &&
      (!produtoSelecionado || l.produto === produtoSelecionado) &&
      (ignorarMunicipio || !municipioSelecionado || l.municipio === municipioSelecionado)
  );
}
const linhasSemMunicipio = aplicarFiltros(true);
const linhasTabelaBase = aplicarFiltros(false);
```

<div class="mapa-card">${mapaRegionalizacao(geojson, linhasSemMunicipio, municipioSelecionado)}</div>

```js
const LIMITE_TABELA = 2000;
const totais = new Map();
for (const l of linhasTabelaBase) {
  const chave = `${l.acao_label}|${l.produto}|${l.unidade_medida}|${l.regiao}|${l.municipio}`;
  const atual = totais.get(chave);
  if (atual) {
    atual.fisica += l.fisica;
    atual.valor += l.valor;
  } else {
    totais.set(chave, { ...l });
  }
}
const totalLinhas = totais.size;
const linhasOrdenadas = [...totais.values()].sort((a, b) => b.valor - a.valor);
const linhasTabela = linhasOrdenadas.slice(0, LIMITE_TABELA);
const aviso =
  totalLinhas > LIMITE_TABELA
    ? `Mostrando as ${LIMITE_TABELA} linhas de maior valor, de um total de ${totalLinhas}. Use os filtros para refinar.`
    : null;
const avisoEl = document.createElement("p");
avisoEl.className = "subtitulo";
avisoEl.textContent = aviso ?? "";
```

${avisoEl}

${tabela(linhasTabela, [
  {chave: "acao_label", rotulo: "Ação Orçamentária"},
  {chave: "produto", rotulo: "Produto"},
  {chave: "unidade_medida", rotulo: "Unidade de Medida"},
  {chave: "regiao", rotulo: "Região Geográfica Intermediária"},
  {chave: "municipio", rotulo: "Município"},
  {chave: "fisica", rotulo: "Previsão Física 2027", formatar: formatarInteiro},
  {chave: "valor", rotulo: "Previsão Orçamentária 2027", formatar: formatarMoeda}
], {nomeArquivo: "regionalizacao", classeExtra: "tabela-regionalizacao"})}
