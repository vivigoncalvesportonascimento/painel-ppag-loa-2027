// Construtores de gráfico Observable Plot reaproveitados por várias
// páginas — equivalentes a graficos.py (grafico_percentual_horizontal /
// grafico_absoluto_vertical) do site estático, mesma cor de marca (#0047AB).

import * as Plot from "../../_node/@observablehq/plot@0.6.17/index.3e99bd70.js";
import { agruparEPercentual, agruparEOrdenar, formatarBiArredondado } from "./utils.de81ded4.js";

const COR_MARCA = "#0047AB";

// Barras verticais, uma por ano (Ação Orçamentária: Previsão Física/
// Orçamentária 2027-2030). `dados` é [{ano, valor}]; `formatar` formata o
// rótulo de cada barra.
export function graficoPorAno(dados, formatar, { width } = {}) {
  const valorMax = Math.max(0, ...dados.map((d) => d.valor));
  return Plot.plot({
    width,
    height: 300,
    marginBottom: 40,
    x: { label: null, domain: dados.map((d) => d.ano) },
    y: { label: null, grid: true, domain: [0, valorMax > 0 ? valorMax * 1.2 : 1] },
    marks: [
      Plot.barY(dados, { x: "ano", y: "valor", fill: COR_MARCA }),
      Plot.text(dados, { x: "ano", y: "valor", text: (d) => formatar(d.valor), dy: -8, fontSize: 12 })
    ]
  });
}

// Barras horizontais com o % do total de `colunaValor` por `coluna`.
export function graficoPercentualHorizontal(linhas, coluna, colunaValor, { width } = {}) {
  const dados = agruparEPercentual(linhas, coluna, colunaValor).sort(
    (a, b) => b.percentual - a.percentual
  );
  const altura = Math.max(260, 30 * dados.length + 40);
  return Plot.plot({
    width,
    height: altura,
    marginLeft: 280,
    marginRight: 50,
    x: { label: "% do total", grid: true, percent: false },
    y: { label: null, domain: dados.map((d) => d.label) },
    marks: [
      Plot.barX(dados, { x: "percentual", y: "label", fill: COR_MARCA }),
      Plot.text(dados, {
        x: "percentual",
        y: "label",
        text: (d) => `${d.percentual.toFixed(1)}%`,
        dx: 6,
        textAnchor: "start",
        fontSize: 11
      })
    ]
  });
}

// Barras horizontais com a soma absoluta de `colunaValor` por `coluna`,
// rótulo em "N bi" (arredondado), ordenado do maior para o menor.
export function graficoAbsolutoHorizontal(linhas, coluna, colunaValor, { width } = {}) {
  const dados = agruparEOrdenar(linhas, coluna, colunaValor).reverse();
  const altura = Math.max(260, 30 * dados.length + 40);
  return Plot.plot({
    width,
    height: altura,
    marginLeft: 220,
    marginRight: 50,
    x: { label: "Valor (R$)", grid: true },
    y: { label: null, domain: dados.map((d) => d.label) },
    marks: [
      Plot.barX(dados, { x: "valor", y: "label", fill: COR_MARCA }),
      Plot.text(dados, {
        x: "valor",
        y: "label",
        text: (d) => formatarBiArredondado(d.valor),
        dx: 6,
        textAnchor: "start",
        fontSize: 11
      })
    ]
  });
}

// Colunas verticais com a soma absoluta de `colunaValor` por `coluna`,
// rótulo em "N bi" (arredondado), ordenado da maior para a menor.
export function graficoAbsolutoVertical(linhas, coluna, colunaValor, { width } = {}) {
  const dados = agruparEOrdenar(linhas, coluna, colunaValor);
  return Plot.plot({
    width,
    height: 340,
    marginBottom: 70,
    x: { label: null, tickRotate: -20 },
    y: { label: "Valor (R$)", grid: true },
    marks: [
      Plot.barY(dados, { x: "label", y: "valor", fill: COR_MARCA }),
      Plot.text(dados, {
        x: "label",
        y: "valor",
        text: (d) => formatarBiArredondado(d.valor),
        dy: -8,
        fontSize: 11
      })
    ]
  });
}
