// Input customizado "select pesquisável": mesmo componente do site estático
// (script.js: tornarFiltroPesquisavel), portado para o protocolo de view do
// Observable Framework (elemento com `.value` + evento "input").
//
// Uso numa página .md:
//   const uo = view(filtroPesquisavel(listaDeUOs, {label: "Unidade Orçamentária"}));

function normalizarTexto(texto) {
  return texto
    .toString()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();
}

export function filtroPesquisavel(
  opcoes,
  { label = "", placeholder = "Todas", value: valorInicial = "" } = {}
) {
  const wrapper = document.createElement("div");
  wrapper.className = "filtro-campo filtro-pesquisavel";
  wrapper.value = valorInicial;

  if (label) {
    const rotulo = document.createElement("label");
    rotulo.textContent = label;
    wrapper.appendChild(rotulo);
  }

  const caixa = document.createElement("div");
  caixa.className = "filtro-pesquisavel-caixa";

  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "filtro-pesquisavel-botao";
  botao.textContent = valorInicial || placeholder;

  const painel = document.createElement("div");
  painel.className = "filtro-pesquisavel-painel";

  const busca = document.createElement("input");
  busca.type = "text";
  busca.placeholder = "Pesquisar";
  busca.className = "filtro-pesquisavel-busca";

  const lista = document.createElement("div");
  lista.className = "filtro-pesquisavel-lista";

  painel.append(busca, lista);
  caixa.append(botao, painel);
  wrapper.appendChild(caixa);

  function escolher(valor) {
    wrapper.value = valor;
    botao.textContent = valor || placeholder;
    wrapper.dispatchEvent(new Event("input", { bubbles: true }));
    fechar();
  }

  function construirLista(filtro) {
    lista.replaceChildren();
    const termo = normalizarTexto(filtro || "");

    const itemTodas = document.createElement("div");
    itemTodas.className = "filtro-pesquisavel-opcao";
    itemTodas.textContent = placeholder;
    if (!wrapper.value) itemTodas.classList.add("selecionada");
    itemTodas.addEventListener("click", () => escolher(""));
    if (!termo || normalizarTexto(placeholder).includes(termo)) lista.appendChild(itemTodas);

    for (const opcao of opcoes) {
      if (termo && !normalizarTexto(opcao).includes(termo)) continue;
      const item = document.createElement("div");
      item.className = "filtro-pesquisavel-opcao";
      item.textContent = opcao;
      if (opcao === wrapper.value) item.classList.add("selecionada");
      item.addEventListener("click", () => escolher(opcao));
      lista.appendChild(item);
    }

    if (!lista.children.length) {
      const vazio = document.createElement("div");
      vazio.className = "filtro-pesquisavel-vazio";
      vazio.textContent = "Nenhum resultado";
      lista.appendChild(vazio);
    }
  }

  function aoClicarFora(evento) {
    if (!caixa.contains(evento.target)) fechar();
  }

  function abrir() {
    painel.classList.add("aberto");
    busca.value = "";
    construirLista("");
    busca.focus();
    document.addEventListener("click", aoClicarFora, true);
  }

  function fechar() {
    painel.classList.remove("aberto");
    document.removeEventListener("click", aoClicarFora, true);
  }

  botao.addEventListener("click", () => {
    if (painel.classList.contains("aberto")) fechar();
    else abrir();
  });
  busca.addEventListener("input", (evento) => {
    evento.stopPropagation();
    construirLista(busca.value);
  });
  busca.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape") fechar();
  });

  wrapper.resetar = () => escolher("");

  return wrapper;
}

// Linha de filtros + botão "Limpar filtros", que reseta todos os selects
// passados (cada um precisa ter sido criado por filtroPesquisavel()).
//
// Expõe um getter `.value` com os valores atuais de todos os selects (nessa
// ordem) e borbulha o evento "input" de qualquer select filho até este
// container — assim, `Generators.input(linhaFiltros(selects))` entrega um
// único stream reativo com `[valor1, valor2, ...]`, sem precisar de um
// `Generators.input` por filtro nem displayar os elementos de novo (o que
// `view()` faria).
export function linhaFiltros(selects) {
  const container = document.createElement("div");
  container.className = "filtros";
  container.append(...selects);

  Object.defineProperty(container, "value", {
    get: () => selects.map((select) => select.value)
  });

  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "botao-secundario";
  botao.textContent = "Limpar filtros";
  botao.addEventListener("click", () => {
    for (const select of selects) select.resetar();
  });
  container.appendChild(botao);

  return container;
}
