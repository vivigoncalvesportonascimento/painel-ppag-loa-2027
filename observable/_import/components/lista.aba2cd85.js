// "Multi-row card" estilo Power BI: título + lista rolável de label/valor
// (usado em Despesa por Órgão: Ação Orçamentária, Fonte de Recursos).
export function listaCartao(titulo, itens) {
  const card = document.createElement("div");
  card.className = "lista-cartao";

  const h3 = document.createElement("h3");
  h3.className = "lista-cartao-titulo";
  h3.textContent = titulo;
  card.appendChild(h3);

  const corpo = document.createElement("div");
  corpo.className = "lista-cartao-corpo";
  for (const item of itens) {
    const linha = document.createElement("div");
    linha.className = "lista-cartao-item";
    const label = document.createElement("span");
    label.className = "label";
    label.textContent = item.label;
    const valor = document.createElement("span");
    valor.className = "valor";
    valor.textContent = item.valor;
    linha.append(label, valor);
    corpo.appendChild(linha);
  }
  card.appendChild(corpo);
  return card;
}
