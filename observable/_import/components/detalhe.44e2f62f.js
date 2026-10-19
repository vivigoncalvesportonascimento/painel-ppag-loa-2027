// Cards de "rótulo + valor" usados nas páginas de detalhe (Ação
// Orçamentária, Programa): um card em destaque (o item selecionado) e
// grades de cards menores com os demais atributos.
export function acaoCard(rotulo, valor, { destaque = false } = {}) {
  const card = document.createElement("div");
  card.className = destaque ? "acao-card acao-card--destaque" : "acao-card";
  const rotuloEl = document.createElement("div");
  rotuloEl.className = "rotulo";
  rotuloEl.textContent = rotulo;
  const valorEl = document.createElement("div");
  valorEl.className = "valor";
  if (Array.isArray(valor)) {
    const ul = document.createElement("ul");
    ul.className = "lista-simples";
    for (const item of valor) {
      const li = document.createElement("li");
      li.textContent = item;
      ul.appendChild(li);
    }
    valorEl.appendChild(ul);
  } else {
    valorEl.textContent = valor;
  }
  card.append(rotuloEl, valorEl);
  return card;
}

export function gradeAcao(cards, variante) {
  const grade = document.createElement("div");
  grade.className = `grade-acao grade-acao--${variante}`;
  grade.append(...cards);
  return grade;
}
