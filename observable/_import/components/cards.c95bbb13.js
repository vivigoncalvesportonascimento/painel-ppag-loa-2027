// Grade de cards de KPI (valor + título), reaproveitada em várias páginas.
export function gradeCards(cards) {
  const container = document.createElement("div");
  container.className = "grade-cards";
  for (const card of cards) {
    const elemento = document.createElement("div");
    elemento.className = "card";
    const valor = document.createElement("div");
    valor.className = "valor";
    valor.textContent = card.valor;
    const titulo = document.createElement("div");
    titulo.className = "titulo";
    titulo.textContent = card.titulo;
    elemento.append(valor, titulo);
    container.appendChild(elemento);
  }
  return container;
}

export function cardUnico(valor, titulo) {
  const elemento = document.createElement("div");
  elemento.className = "card";
  const valorEl = document.createElement("div");
  valorEl.className = "valor";
  valorEl.textContent = valor;
  const tituloEl = document.createElement("div");
  tituloEl.className = "titulo";
  tituloEl.textContent = titulo;
  elemento.append(valorEl, tituloEl);
  return elemento;
}
