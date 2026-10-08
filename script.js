document.querySelectorAll(".menu-item").forEach((botao) => {
  botao.addEventListener("click", () => {
    document.querySelectorAll(".menu-item").forEach((b) => {
      b.classList.remove("ativo");
      b.setAttribute("aria-selected", "false");
    });
    document.querySelectorAll(".pagina").forEach((p) => p.classList.remove("ativa"));

    botao.classList.add("ativo");
    botao.setAttribute("aria-selected", "true");
    document.getElementById(botao.dataset.pagina).classList.add("ativa");
  });
});

fetch("dados.json")
  .then((resposta) => resposta.json())
  .then((dados) => {
    renderizarCards(dados.cards);
    Plotly.newPlot("grafico-area-tematica", dados.grafico_area_tematica.data, dados.grafico_area_tematica.layout, {
      responsive: true,
      displayModeBar: false,
    });
    Plotly.newPlot("grafico-setor-governo", dados.grafico_setor_governo.data, dados.grafico_setor_governo.layout, {
      responsive: true,
      displayModeBar: false,
    });
  })
  .catch((erro) => {
    document.getElementById("cards").innerHTML =
      '<p class="carregando">Não foi possível carregar os dados.</p>';
    console.error(erro);
  });

function renderizarCards(cards) {
  const container = document.getElementById("cards");
  container.replaceChildren();
  cards.forEach((card) => {
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
  });
}
