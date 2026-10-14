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

    inicializarReceitaFiscal(dados.receita_fiscal.linhas);

    document.getElementById("despesa-total-valor").textContent =
      dados.despesa_fiscal.card_despesa_total;
    Plotly.newPlot(
      "grafico-despesa-poder",
      dados.despesa_fiscal.grafico_poder.data,
      dados.despesa_fiscal.grafico_poder.layout,
      { responsive: true, displayModeBar: false }
    );
    Plotly.newPlot(
      "grafico-despesa-grupo",
      dados.despesa_fiscal.grafico_grupo.data,
      dados.despesa_fiscal.grafico_grupo.layout,
      { responsive: true, displayModeBar: false }
    );
    Plotly.newPlot(
      "grafico-despesa-funcao",
      dados.despesa_fiscal.grafico_funcao.data,
      dados.despesa_fiscal.grafico_funcao.layout,
      { responsive: true, displayModeBar: false }
    );

    inicializarDespesaOrgao(dados.despesa_orgao.linhas);
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

function inicializarReceitaFiscal(linhas) {
  const selectUo = document.getElementById("filtro-uo");
  const selectFonte = document.getElementById("filtro-fonte");

  popularOpcoes(selectUo, [...new Set(linhas.map((l) => l.UO))].sort());
  popularOpcoes(selectFonte, [...new Set(linhas.map((l) => l.fonte_de_recursos))].sort());

  const atualizar = () => {
    const uo = selectUo.value;
    const fonte = selectFonte.value;
    const filtradas = linhas.filter(
      (l) => (!uo || l.UO === uo) && (!fonte || l.fonte_de_recursos === fonte)
    );
    atualizarCardReceita(filtradas);
    atualizarGraficoReceitaCategoria(filtradas);
    atualizarTabelaUoFonte(filtradas);
  };

  selectUo.addEventListener("change", atualizar);
  selectFonte.addEventListener("change", atualizar);

  document.getElementById("limpar-filtros").addEventListener("click", () => {
    selectUo.value = "";
    selectFonte.value = "";
    atualizar();
  });

  atualizar();
}

function popularOpcoes(select, valores) {
  valores.forEach((valor) => {
    const option = document.createElement("option");
    option.value = valor;
    option.textContent = valor;
    select.appendChild(option);
  });
}

function somar(linhas) {
  return linhas.reduce((total, linha) => total + linha.valor, 0);
}

function formatarBi(valor) {
  const bilhoes = valor / 1_000_000_000;
  const truncado = Math.floor(bilhoes * 10) / 10;
  return `R$ ${truncado.toFixed(1).replace(".", ",")} bi`;
}

function formatarBiArredondado(valor) {
  return `${Math.round(valor / 1_000_000_000)} bi`;
}

function formatarMoeda(valor) {
  return `R$ ${valor.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function atualizarCardReceita(linhas) {
  document.getElementById("receita-total-valor").textContent = formatarBi(somar(linhas));
}

function atualizarGraficoReceitaCategoria(linhas) {
  const totais = new Map();
  linhas.forEach((linha) => {
    totais.set(
      linha.categoria_receita_desc,
      (totais.get(linha.categoria_receita_desc) || 0) + linha.valor
    );
  });

  const categorias = [...totais.entries()].sort((a, b) => a[1] - b[1]);
  const valores = categorias.map((c) => c[1]);
  const valorMin = Math.min(0, ...valores);
  const valorMax = Math.max(...valores);
  const margem = (valorMax - valorMin) * 0.15;

  const data = [
    {
      type: "bar",
      orientation: "h",
      x: valores,
      y: categorias.map((c) => c[0]),
      text: categorias.map((c) => formatarBiArredondado(c[1])),
      textposition: "outside",
      textfont: { size: 15 },
      cliponaxis: false,
      marker: { color: "#0047AB" },
    },
  ];

  const layout = {
    title: { text: "<b>Receitas por Categoria Econômica</b>", font: { size: 16, color: "#1f2933" } },
    showlegend: false,
    height: 280,
    font: { family: "system-ui, -apple-system, Segoe UI, Arial, sans-serif", color: "#1f2933" },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 10, r: 40, t: 40, b: 10 },
    yaxis: { tickfont: { size: 12 }, automargin: true },
    xaxis: { gridcolor: "#eef1f4", range: [valorMin - margem, valorMax + margem] },
  };

  Plotly.newPlot("grafico-receita-categoria", data, layout, {
    responsive: true,
    displayModeBar: false,
  });
}

function atualizarTabelaUoFonte(linhas) {
  const totais = new Map();
  linhas.forEach((linha) => {
    const chave = `${linha.UO}|${linha.fonte_de_recursos}`;
    const atual = totais.get(chave);
    if (atual) {
      atual.valor += linha.valor;
    } else {
      totais.set(chave, { UO: linha.UO, fonte: linha.fonte_de_recursos, valor: linha.valor });
    }
  });

  const linhasOrdenadas = [...totais.values()].sort((a, b) => b.valor - a.valor);

  const corpo = document.getElementById("tabela-uo-fonte-corpo");
  corpo.replaceChildren();

  if (linhasOrdenadas.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.className = "carregando";
    td.textContent = "Nenhum dado para os filtros selecionados.";
    tr.appendChild(td);
    corpo.appendChild(tr);
    return;
  }

  linhasOrdenadas.forEach((linha) => {
    const tr = document.createElement("tr");
    [linha.UO, linha.fonte, formatarMoeda(linha.valor)].forEach((valor) => {
      const td = document.createElement("td");
      td.textContent = valor;
      tr.appendChild(td);
    });
    corpo.appendChild(tr);
  });
}

function inicializarDespesaOrgao(linhas) {
  const selectUo = document.getElementById("filtro-uo-orgao");
  popularOpcoes(selectUo, [...new Set(linhas.map((l) => l.uo_label))].sort());

  const atualizar = () => {
    const uo = selectUo.value;
    const filtradas = linhas.filter((l) => !uo || l.uo_label === uo);

    document.getElementById("despesa-orgao-total-valor").textContent = formatarBi(
      somar(filtradas)
    );
    atualizarGraficoDespesaOrgaoGrupo(filtradas);
    renderizarListaCartao("lista-acao", agruparEOrdenar(filtradas, "acao_label", formatarMoeda));
    renderizarListaCartao(
      "lista-fonte",
      agruparEOrdenarPercentual(filtradas, "fonte_label")
    );
  };

  selectUo.addEventListener("change", atualizar);

  document.getElementById("limpar-filtros-orgao").addEventListener("click", () => {
    selectUo.value = "";
    atualizar();
  });

  atualizar();
}

function agruparEOrdenar(linhas, coluna, formatar) {
  const totais = new Map();
  linhas.forEach((linha) => {
    totais.set(linha[coluna], (totais.get(linha[coluna]) || 0) + linha.valor);
  });
  return [...totais.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([label, valor]) => ({ label, valor: formatar(valor) }));
}

function agruparEOrdenarPercentual(linhas, coluna) {
  const totais = new Map();
  linhas.forEach((linha) => {
    totais.set(linha[coluna], (totais.get(linha[coluna]) || 0) + linha.valor);
  });
  const total = [...totais.values()].reduce((soma, v) => soma + v, 0);
  return [...totais.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([label, valor]) => ({
      label,
      valor: `${((valor / total) * 100).toFixed(1)}%`,
    }));
}

function renderizarListaCartao(elementId, itens) {
  const container = document.getElementById(elementId);
  container.replaceChildren();

  if (itens.length === 0) {
    const vazio = document.createElement("p");
    vazio.className = "carregando";
    vazio.textContent = "Nenhum dado para os filtros selecionados.";
    container.appendChild(vazio);
    return;
  }

  itens.forEach((item) => {
    const linha = document.createElement("div");
    linha.className = "lista-cartao-item";

    const label = document.createElement("div");
    label.className = "label";
    label.textContent = item.label;

    const valor = document.createElement("div");
    valor.className = "valor";
    valor.textContent = item.valor;

    linha.append(label, valor);
    container.appendChild(linha);
  });
}

function atualizarGraficoDespesaOrgaoGrupo(linhas) {
  const totais = new Map();
  linhas.forEach((linha) => {
    totais.set(
      linha.grupo_despesa_descricao,
      (totais.get(linha.grupo_despesa_descricao) || 0) + linha.valor
    );
  });

  const categorias = [...totais.entries()].sort((a, b) => b[1] - a[1]);
  const valores = categorias.map((c) => c[1]);
  const valorMax = Math.max(...valores, 0);

  const data = [
    {
      type: "bar",
      x: categorias.map((c) => c[0]),
      y: valores,
      text: categorias.map((c) => formatarBiArredondado(c[1])),
      textposition: "outside",
      textfont: { size: 13 },
      cliponaxis: false,
      marker: { color: "#0047AB" },
    },
  ];

  const layout = {
    title: { text: "<b>Despesa por Grupo</b>", font: { size: 16, color: "#1f2933" } },
    showlegend: false,
    height: 340,
    font: { family: "system-ui, -apple-system, Segoe UI, Arial, sans-serif", color: "#1f2933" },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 10, r: 10, t: 50, b: 90 },
    xaxis: { tickfont: { size: 11 }, tickangle: -25, automargin: true },
    yaxis: { gridcolor: "#eef1f4", range: [0, valorMax * 1.18] },
  };

  Plotly.newPlot("grafico-despesa-orgao-grupo", data, layout, {
    responsive: true,
    displayModeBar: false,
  });
}
