---
toc: false
---

# Despesa Fiscal

```js
import { cardUnico } from "./components/cards.js";
import { graficoAbsolutoVertical, graficoPercentualHorizontal } from "./components/graficos.js";
import { formatarBi } from "./components/utils.js";

const dados = await FileAttachment("data/dados.json").json();
const despesaFiscal = dados.despesa_fiscal;
```

<div class="linha-card-grafico">
  <div>${cardUnico(formatarBi(despesaFiscal.card_total), "Despesa Total (R$) - 2027")}</div>
  <div class="grafico-card">${graficoAbsolutoVertical(despesaFiscal.linhas_poder, "uo_poder", "valor")}</div>
</div>

<div class="grade-graficos">
  <div class="grafico-card">${graficoPercentualHorizontal(despesaFiscal.linhas_grupo, "grupo_despesa_descricao", "valor")}</div>
  <div class="grafico-card">${graficoPercentualHorizontal(despesaFiscal.linhas_funcao, "funcao_descricao", "valor")}</div>
</div>
