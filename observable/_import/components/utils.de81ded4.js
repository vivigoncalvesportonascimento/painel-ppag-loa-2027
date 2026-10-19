// Formatação compartilhada entre as páginas — mesmas regras do utils.py /
// script.js do site estático (ver docs/premissas.md no repositório).

export function formatarMoeda(valor) {
  return `R$ ${Number(valor).toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
}

export function formatarBi(valor) {
  if (Math.abs(valor) >= 1_000_000_000) {
    const bilhoes = valor / 1_000_000_000;
    const truncado = Math.floor(bilhoes * 10) / 10;
    return `R$ ${truncado.toFixed(1).replace(".", ",")} bi`;
  }
  const milhoes = valor / 1_000_000;
  return `R$ ${milhoes.toFixed(2).replace(".", ",")} Mi`;
}

export function formatarBiArredondado(valor) {
  return `${Math.round(valor / 1_000_000_000)} bi`;
}

export function formatarInteiro(valor) {
  return Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: 0 });
}

// Agrupa `linhas` por `coluna` somando `colunaValor`; retorna [{label, valor}]
// ordenado do maior para o menor (mesma lógica de agruparEOrdenar no script.js).
export function agruparEOrdenar(linhas, coluna, colunaValor = "valor") {
  const totais = new Map();
  for (const linha of linhas) {
    const chave = linha[coluna];
    totais.set(chave, (totais.get(chave) || 0) + linha[colunaValor]);
  }
  return [...totais.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([label, valor]) => ({ label, valor }));
}

// Mesma agregação, mas retorna o percentual do total (0-100) em vez do valor
// absoluto — usado nos gráficos horizontais (Visão Geral, Despesa Fiscal/Órgão).
export function agruparEPercentual(linhas, coluna, colunaValor = "valor") {
  const agregado = agruparEOrdenar(linhas, coluna, colunaValor);
  const total = agregado.reduce((soma, item) => soma + item.valor, 0);
  return agregado
    .map((item) => ({ label: item.label, percentual: (item.valor / total) * 100 }))
    .sort((a, b) => a.percentual - b.percentual);
}
