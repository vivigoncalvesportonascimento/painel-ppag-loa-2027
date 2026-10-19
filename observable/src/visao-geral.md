---
toc: false
---

# Visão Geral

<p class="subtitulo">Dados gerais do orçamento 2027</p>

```js
import { gradeCards } from "./components/cards.js";
import { graficoPercentualHorizontal } from "./components/graficos.js";
import { formatarBi, formatarInteiro } from "./components/utils.js";

const dados = await FileAttachment("data/dados.json").json();
const c = dados.cards;
const cards = [
  { titulo: "Previsão 2027 - Orçamento Fiscal", valor: formatarBi(c.total_fiscal) },
  { titulo: "Previsão 2027 - Orçamento de Investimentos", valor: formatarBi(c.total_investimento) },
  { titulo: "Quantidade de Programas", valor: formatarInteiro(c.qtd_programas) },
  { titulo: "Quantidade de Ações", valor: formatarInteiro(c.qtd_acoes) },
  { titulo: "Projetos Estratégicos", valor: formatarInteiro(c.qtd_projetos_estrategicos) }
];
```

${gradeCards(cards)}

<div class="grade-graficos">
  <div class="grafico-card">${graficoPercentualHorizontal(dados.visao_geral.linhas, "area_tematica", "valor")}</div>
  <div class="grafico-card">${graficoPercentualHorizontal(dados.visao_geral.linhas, "setor_governo", "valor")}</div>
</div>
