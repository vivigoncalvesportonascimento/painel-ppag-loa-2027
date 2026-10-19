---
toc: false
---

# Glossário

```js
const dados = await FileAttachment("data/dados.json").json();
const termos = dados.glossario;

const nuvem = document.createElement("div");
nuvem.className = "glossario-nuvem";

const painelTecnico = document.createElement("div");
painelTecnico.className = "glossario-painel";
painelTecnico.innerHTML = "<h4>Definição Técnica</h4><p></p>";

const painelSimples = document.createElement("div");
painelSimples.className = "glossario-painel";
painelSimples.innerHTML = "<h4>Linguagem Simples</h4><p></p>";

function selecionar(indice) {
  [...nuvem.children].forEach((botao, i) => botao.classList.toggle("ativo", i === indice));
  const item = termos[indice];
  painelTecnico.querySelector("p").textContent = item.definicao_tecnica;
  painelSimples.querySelector("p").textContent = item.linguagem_simples;
}

termos.forEach((item, indice) => {
  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "termo-botao";
  botao.textContent = item.termo;
  botao.addEventListener("click", () => selecionar(indice));
  nuvem.appendChild(botao);
});

if (termos.length) selecionar(0);

display(nuvem);
display(painelTecnico);
display(painelSimples);
```
