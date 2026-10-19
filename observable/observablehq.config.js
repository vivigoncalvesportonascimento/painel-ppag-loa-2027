export default {
  root: "src",
  title: "Painel PPAG-LOA 2027",
  pages: [
    {name: "Sobre o Painel", path: "/"},
    {name: "Visão Geral", path: "/visao-geral"},
    {name: "Ação Orçamentária", path: "/acao-orcamentaria"},
    {name: "Programa", path: "/programa"},
    {name: "Regionalização", path: "/regionalizacao"},
    {name: "Receita Fiscal", path: "/receita-fiscal"},
    {name: "Despesa Fiscal", path: "/despesa-fiscal"},
    {name: "Despesa por Órgão", path: "/despesa-por-orgao"},
    {name: "QDD", path: "/qdd"},
    {name: "LOA Investimentos", path: "/loa-investimentos"},
    {name: "Glossário", path: "/glossario"},
    {name: "Links Úteis", path: "/links-uteis"}
  ],
  theme: ["air", "wide"],
  header: '<div class="marca-painel">Painel PPAG-LOA 2027</div>',
  footer:
    'Construído com <a href="https://observablehq.com/framework/" target="_blank" rel="noopener noreferrer">Observable Framework</a> — versão de comparação do <a href="https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/" target="_blank" rel="noopener noreferrer">painel publicado no GitHub Pages</a>.',
  toc: false,
  pager: false,
  base: "/painel-ppag-loa-2027/observable/",
  head: '<link rel="stylesheet" href="custom-style.css">',
  interpreters: {
    ".py": ["C:/projects/painel-ppag-loa-2027/.venv/Scripts/python.exe"]
  }
};
