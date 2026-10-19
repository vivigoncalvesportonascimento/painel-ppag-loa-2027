// Tabela HTML genérica com colunas redimensionáveis (igual ao site
// estático: CSS `resize: horizontal` nos <th>) e botões de exportação
// CSV/Excel que exportam exatamente o que está sendo exibido (mesmos
// rótulos de coluna e valores já formatados).
import { botoesExportar } from "./exportar.js";

// colunas: [{chave, rotulo, formatar?}] — `formatar` recebe o valor bruto da
// linha e devolve o texto a exibir (e a exportar); se omitido, usa o valor
// bruto como está.
export function tabela(linhas, colunas, { nomeArquivo, classeExtra = "", semResultadoTexto = "Nenhum dado para os filtros selecionados." } = {}) {
  const card = document.createElement("div");
  card.className = "tabela-card";

  const linhasFormatadas = linhas.map((linha) => {
    const saida = {};
    for (const coluna of colunas) {
      const valor = linha[coluna.chave];
      saida[coluna.rotulo] = coluna.formatar ? coluna.formatar(valor, linha) : valor;
    }
    return saida;
  });

  card.appendChild(botoesExportar(linhasFormatadas, nomeArquivo));

  const scroll = document.createElement("div");
  scroll.className = "tabela-scroll";

  const table = document.createElement("table");
  table.className = `tabela-redimensionavel ${classeExtra}`.trim();

  const thead = document.createElement("thead");
  const trCabecalho = document.createElement("tr");
  for (const coluna of colunas) {
    const th = document.createElement("th");
    th.textContent = coluna.rotulo;
    trCabecalho.appendChild(th);
  }
  thead.appendChild(trCabecalho);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  if (!linhasFormatadas.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = colunas.length;
    td.style.textAlign = "center";
    td.style.color = "var(--theme-foreground-muted)";
    td.textContent = semResultadoTexto;
    tr.appendChild(td);
    tbody.appendChild(tr);
  } else {
    for (const linha of linhasFormatadas) {
      const tr = document.createElement("tr");
      for (const coluna of colunas) {
        const td = document.createElement("td");
        td.textContent = linha[coluna.rotulo];
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
  }
  table.appendChild(tbody);

  scroll.appendChild(table);
  card.appendChild(scroll);
  return card;
}
