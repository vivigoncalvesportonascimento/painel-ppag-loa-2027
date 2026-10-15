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

    if (botao.dataset.pagina === "regionalizacao") {
      carregarRegionalizacao();
    }
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

    inicializarLoaInvestimentos(
      dados.loa_investimentos.uo_opcoes,
      dados.loa_investimentos.linhas_receita,
      dados.loa_investimentos.linhas_despesa
    );

    inicializarGlossario(dados.glossario);
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
  if (Math.abs(valor) >= 1_000_000_000) {
    const bilhoes = valor / 1_000_000_000;
    const truncado = Math.floor(bilhoes * 10) / 10;
    return `R$ ${truncado.toFixed(1).replace(".", ",")} bi`;
  }

  const milhoes = valor / 1_000_000;
  return `R$ ${milhoes.toFixed(2).replace(".", ",")} Mi`;
}

function formatarBiArredondado(valor) {
  return `${Math.round(valor / 1_000_000_000)} bi`;
}

function quebrarRotulo(texto, largura = 14) {
  const palavras = texto.split(" ");
  const linhas = [];
  let linhaAtual = "";

  palavras.forEach((palavra) => {
    const candidata = linhaAtual ? `${linhaAtual} ${palavra}` : palavra;
    if (candidata.length > largura && linhaAtual) {
      linhas.push(linhaAtual);
      linhaAtual = palavra;
    } else {
      linhaAtual = candidata;
    }
  });
  if (linhaAtual) {
    linhas.push(linhaAtual);
  }

  return linhas.join("<br>");
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
      x: categorias.map((c) => quebrarRotulo(c[0])),
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
    margin: { l: 10, r: 10, t: 50, b: 70 },
    xaxis: { tickfont: { size: 10 }, tickangle: 0, automargin: true },
    yaxis: { gridcolor: "#eef1f4", range: [0, valorMax * 1.18] },
  };

  Plotly.newPlot("grafico-despesa-orgao-grupo", data, layout, {
    responsive: true,
    displayModeBar: false,
  });
}

function inicializarLoaInvestimentos(uoOpcoes, linhasReceita, linhasDespesa) {
  const select = document.getElementById("filtro-uo-investimentos");
  popularOpcoes(select, uoOpcoes);

  const atualizar = () => {
    const uo = select.value;
    const receitaFiltrada = linhasReceita.filter((l) => !uo || l.uo_label === uo);
    const despesaFiltrada = linhasDespesa.filter((l) => !uo || l.uo_label === uo);

    document.getElementById("investimentos-receita-valor").textContent = formatarBi(
      somar(receitaFiltrada)
    );
    document.getElementById("investimentos-despesa-valor").textContent = formatarBi(
      somar(despesaFiltrada)
    );
    atualizarTabelaInvestimentos(despesaFiltrada);
  };

  select.addEventListener("change", atualizar);

  document.getElementById("limpar-filtros-investimentos").addEventListener("click", () => {
    select.value = "";
    atualizar();
  });

  atualizar();
}

function atualizarTabelaInvestimentos(linhas) {
  const totais = new Map();
  linhas.forEach((linha) => {
    const chave = `${linha.uo_sigla}|${linha.acao_label}`;
    const atual = totais.get(chave);
    if (atual) {
      atual.valor += linha.valor;
    } else {
      totais.set(chave, {
        uo_sigla: linha.uo_sigla,
        acao_label: linha.acao_label,
        valor: linha.valor,
      });
    }
  });

  const linhasOrdenadas = [...totais.values()].sort((a, b) => b.valor - a.valor);

  const corpo = document.getElementById("tabela-investimentos-corpo");
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
    [linha.uo_sigla, linha.acao_label, formatarMoeda(linha.valor)].forEach((valor) => {
      const td = document.createElement("td");
      td.textContent = valor;
      tr.appendChild(td);
    });
    corpo.appendChild(tr);
  });
}

let _regionalizacaoCarregada = false;
let _regionalizacaoLinhas = null;
let _regionalizacaoGeojson = null;
let _regionalizacaoUniverso = null;
let _regionalizacaoNomeParaIbge = null;
let _regionalizacaoIbgeParaNome = null;

const LIMITE_TABELA_REGIONALIZACAO = 2000;

function decodificarLinhasRegionalizacao(dadosReg) {
  const { uo, acao, regiao, produto, unidade, municipios, linhas } = dadosReg;
  const total = linhas.valor.length;
  const resultado = new Array(total);

  for (let i = 0; i < total; i += 1) {
    const municipio = municipios[linhas.municipio[i]];
    resultado[i] = {
      uo_label: uo[linhas.uo[i]],
      acao_label: acao[linhas.acao[i]],
      regiao: regiao[linhas.regiao[i]],
      produto: produto[linhas.produto[i]],
      unidade_medida: unidade[linhas.unidade[i]],
      municipio: municipio.nome,
      municipio_ibge: municipio.ibge,
      fisica: linhas.fisica[i],
      valor: linhas.valor[i],
    };
  }

  return resultado;
}

function carregarRegionalizacao() {
  if (_regionalizacaoCarregada) {
    return;
  }
  _regionalizacaoCarregada = true;

  Promise.all([
    fetch("dados_regionalizacao.json").then((r) => r.json()),
    fetch("mg_municipios.geojson").then((r) => r.json()),
  ])
    .then(([dadosReg, geojson]) => {
      _regionalizacaoLinhas = decodificarLinhasRegionalizacao(dadosReg);
      _regionalizacaoGeojson = geojson;
      _regionalizacaoUniverso = geojson.features.map((f) => ({
        municipio_ibge: f.properties.id,
        municipio_geo: f.properties.name,
      }));

      _regionalizacaoNomeParaIbge = new Map();
      _regionalizacaoIbgeParaNome = new Map();
      _regionalizacaoLinhas.forEach((l) => {
        _regionalizacaoNomeParaIbge.set(l.municipio, l.municipio_ibge);
        _regionalizacaoIbgeParaNome.set(l.municipio_ibge, l.municipio);
      });
      _regionalizacaoUniverso.forEach((u) => {
        if (!_regionalizacaoIbgeParaNome.has(u.municipio_ibge)) {
          _regionalizacaoIbgeParaNome.set(u.municipio_ibge, u.municipio_geo);
        }
      });

      inicializarFiltrosRegionalizacao();
    })
    .catch((erro) => {
      document.getElementById("tabela-regionalizacao-corpo").innerHTML =
        '<tr><td colspan="7" class="carregando">Não foi possível carregar os dados.</td></tr>';
      console.error(erro);
    });
}

function inicializarFiltrosRegionalizacao() {
  const selectUo = document.getElementById("filtro-regionalizacao-uo");
  const selectAcao = document.getElementById("filtro-regionalizacao-acao");
  const selectRegiao = document.getElementById("filtro-regionalizacao-regiao");
  const selectMunicipio = document.getElementById("filtro-regionalizacao-municipio");
  const selectProduto = document.getElementById("filtro-regionalizacao-produto");

  popularOpcoes(selectUo, [...new Set(_regionalizacaoLinhas.map((l) => l.uo_label))].sort());
  popularOpcoes(selectAcao, [...new Set(_regionalizacaoLinhas.map((l) => l.acao_label))].sort());
  popularOpcoes(selectRegiao, [...new Set(_regionalizacaoLinhas.map((l) => l.regiao))].sort());
  popularOpcoes(
    selectMunicipio,
    [...new Set(_regionalizacaoLinhas.map((l) => l.municipio))].sort()
  );
  popularOpcoes(
    selectProduto,
    [...new Set(_regionalizacaoLinhas.map((l) => l.produto).filter(Boolean))].sort()
  );

  const selects = [selectUo, selectAcao, selectRegiao, selectMunicipio, selectProduto];

  const atualizar = () => {
    const filtros = {
      uo: selectUo.value,
      acao: selectAcao.value,
      regiao: selectRegiao.value,
      municipio: selectMunicipio.value,
      produto: selectProduto.value,
    };

    const baseSemMunicipio = aplicarFiltrosRegionalizacao(_regionalizacaoLinhas, filtros, true);
    const baseTabela = aplicarFiltrosRegionalizacao(_regionalizacaoLinhas, filtros, false);

    atualizarMapaRegionalizacao(baseSemMunicipio, filtros.municipio);
    atualizarTabelaRegionalizacao(baseTabela);
  };

  selects.forEach((select) => select.addEventListener("change", atualizar));

  document.getElementById("limpar-filtros-regionalizacao").addEventListener("click", () => {
    selects.forEach((select) => {
      select.value = "";
    });
    atualizar();
  });

  atualizar();
}

function aplicarFiltrosRegionalizacao(linhas, filtros, ignorarMunicipio) {
  return linhas.filter(
    (l) =>
      (!filtros.uo || l.uo_label === filtros.uo) &&
      (!filtros.acao || l.acao_label === filtros.acao) &&
      (!filtros.regiao || l.regiao === filtros.regiao) &&
      (!filtros.produto || l.produto === filtros.produto) &&
      (ignorarMunicipio || !filtros.municipio || l.municipio === filtros.municipio)
  );
}

function atualizarMapaRegionalizacao(linhas, municipioSelecionado) {
  const valoresPorIbge = new Map();
  linhas.forEach((l) => {
    valoresPorIbge.set(l.municipio_ibge, (valoresPorIbge.get(l.municipio_ibge) || 0) + l.valor);
  });

  const ibgeSelecionado = municipioSelecionado
    ? _regionalizacaoNomeParaIbge.get(municipioSelecionado)
    : null;

  const locations = _regionalizacaoUniverso.map((u) => u.municipio_ibge);
  const z = locations.map((ibge) => (ibge === ibgeSelecionado ? 1 : 0));
  const customdata = locations.map((ibge) => [
    _regionalizacaoIbgeParaNome.get(ibge),
    formatarMoeda(valoresPorIbge.get(ibge) || 0),
  ]);

  const data = [
    {
      type: "choropleth",
      geojson: _regionalizacaoGeojson,
      featureidkey: "properties.id",
      locations,
      z,
      zmin: 0,
      zmax: 1,
      colorscale: [
        [0, "#cbd2d9"],
        [1, "#0047AB"],
      ],
      showscale: false,
      marker: { line: { color: "#ffffff", width: 0.4 } },
      customdata,
      hovertemplate:
        "<b>%{customdata[0]}</b><br>Previsão Orçamentária 2027: %{customdata[1]}<extra></extra>",
    },
  ];

  const layout = {
    height: 540,
    margin: { l: 0, r: 0, t: 10, b: 0 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: "system-ui, -apple-system, Segoe UI, Arial, sans-serif", color: "#1f2933" },
    geo: { fitbounds: "locations", visible: false },
  };

  Plotly.newPlot("mapa-regionalizacao", data, layout, {
    responsive: true,
    displayModeBar: false,
  });
}

function formatarNumero(valor) {
  return valor.toLocaleString("pt-BR", { maximumFractionDigits: 0 });
}

function atualizarTabelaRegionalizacao(linhas) {
  const totais = new Map();
  linhas.forEach((l) => {
    const chave = `${l.acao_label}|${l.produto}|${l.unidade_medida}|${l.regiao}|${l.municipio}`;
    const atual = totais.get(chave);
    if (atual) {
      atual.fisica += l.fisica;
      atual.valor += l.valor;
    } else {
      totais.set(chave, {
        acao_label: l.acao_label,
        produto: l.produto,
        unidade_medida: l.unidade_medida,
        regiao: l.regiao,
        municipio: l.municipio,
        fisica: l.fisica,
        valor: l.valor,
      });
    }
  });

  const linhasOrdenadas = [...totais.values()].sort((a, b) => b.valor - a.valor);

  const corpo = document.getElementById("tabela-regionalizacao-corpo");
  corpo.replaceChildren();

  if (linhasOrdenadas.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 7;
    td.className = "carregando";
    td.textContent = "Nenhum dado para os filtros selecionados.";
    tr.appendChild(td);
    corpo.appendChild(tr);
    return;
  }

  const exibir = linhasOrdenadas.slice(0, LIMITE_TABELA_REGIONALIZACAO);

  exibir.forEach((linha) => {
    const tr = document.createElement("tr");
    [
      linha.acao_label,
      linha.produto,
      linha.unidade_medida,
      linha.regiao,
      linha.municipio,
      formatarNumero(linha.fisica),
      formatarMoeda(linha.valor),
    ].forEach((valor) => {
      const td = document.createElement("td");
      td.textContent = valor;
      tr.appendChild(td);
    });
    corpo.appendChild(tr);
  });

  if (linhasOrdenadas.length > LIMITE_TABELA_REGIONALIZACAO) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 7;
    td.className = "carregando";
    td.textContent = `Mostrando as ${LIMITE_TABELA_REGIONALIZACAO} linhas de maior valor, de um total de ${linhasOrdenadas.length}. Use os filtros para refinar.`;
    tr.appendChild(td);
    corpo.appendChild(tr);
  }
}

function inicializarGlossario(termos) {
  const container = document.getElementById("glossario-nuvem");
  container.replaceChildren();

  termos.forEach((item, indice) => {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className = "termo-botao";
    botao.textContent = item.termo;
    botao.addEventListener("click", () => selecionarTermoGlossario(termos, indice));
    container.appendChild(botao);
  });

  if (termos.length > 0) {
    selecionarTermoGlossario(termos, 0);
  }
}

function selecionarTermoGlossario(termos, indiceSelecionado) {
  const container = document.getElementById("glossario-nuvem");
  [...container.children].forEach((botao, indice) => {
    botao.classList.toggle("ativo", indice === indiceSelecionado);
  });

  const item = termos[indiceSelecionado];
  document.getElementById("glossario-definicao-tecnica").textContent = item.definicao_tecnica;
  document.getElementById("glossario-linguagem-simples").textContent = item.linguagem_simples;
}
