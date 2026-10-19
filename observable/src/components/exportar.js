// Botões de exportação (CSV/Excel) reaproveitados em todas as tabelas,
// mesma técnica do site estático (SheetJS) — incluindo a sanitização contra
// injeção de fórmula CSV/Excel (ver docs/premissas.md / commit de segurança
// do site estático).

import * as XLSX from "xlsx";

const CARACTERES_FORMULA = ["=", "+", "-", "@", "\t", "\r"];

function sanitizarLinha(linha) {
  const saida = {};
  for (const [chave, valor] of Object.entries(linha)) {
    if (typeof valor === "string" && valor.length && CARACTERES_FORMULA.includes(valor[0])) {
      saida[chave] = `'${valor}`;
    } else {
      saida[chave] = valor;
    }
  }
  return saida;
}

function baixarBlob(blob, nomeArquivo) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nomeArquivo;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function exportarCsv(linhas, nomeArquivo) {
  const planilha = XLSX.utils.json_to_sheet(linhas.map(sanitizarLinha));
  const csv = XLSX.utils.sheet_to_csv(planilha, { FS: ";" });
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
  baixarBlob(blob, `${nomeArquivo}.csv`);
}

export function exportarXlsx(linhas, nomeArquivo) {
  const planilha = XLSX.utils.json_to_sheet(linhas.map(sanitizarLinha));
  const livro = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(livro, planilha, "Dados");
  XLSX.writeFile(livro, `${nomeArquivo}.xlsx`);
}

// Retorna um elemento com os dois botões, prontos para `display(...)`.
export function botoesExportar(linhas, nomeArquivo) {
  const container = document.createElement("div");
  container.className = "tabela-exportar";

  const botaoCsv = document.createElement("button");
  botaoCsv.type = "button";
  botaoCsv.className = "botao-exportar";
  botaoCsv.textContent = "Exportar CSV";
  botaoCsv.addEventListener("click", () => exportarCsv(linhas, nomeArquivo));

  const botaoXlsx = document.createElement("button");
  botaoXlsx.type = "button";
  botaoXlsx.className = "botao-exportar";
  botaoXlsx.textContent = "Exportar Excel";
  botaoXlsx.addEventListener("click", () => exportarXlsx(linhas, nomeArquivo));

  container.append(botaoCsv, botaoXlsx);
  return container;
}
