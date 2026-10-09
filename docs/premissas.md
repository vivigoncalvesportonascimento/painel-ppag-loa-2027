# Premissas de tratamento dos dados

## 1. Exclusão lógica de programas, ações e indicadores

Nas bases de planejamento (`programas_planejamento.txt`, `acoes_planejamento.txt`,
`localizadores_todos_planejamento.txt` e `indicadores_planejamento.txt`), algumas
linhas representam programas, ações ou indicadores que foram **logicamente
excluídos** (não devem mais ser considerados), mas que permanecem na base por
motivos de histórico/auditoria.

Como premissa do painel, essas linhas excluídas **não entram em nenhuma
visualização**. O primeiro tratamento aplicado a cada base, implementado em
`etl/limpeza_inicial.py`, filtra:

| Base | Regra de filtro (mantém apenas) |
|---|---|
| `programas_planejamento.txt` | `Exclusão Lógica do Programa` == `Não` |
| `acoes_planejamento.txt` | `Exclusão Lógica do Programa` == `Não` **e** `Exclusão Lógica da Ação` == `Não` |
| `localizadores_todos_planejamento.txt` | `Exclusão Lógica do Programa` == `False` |
| `indicadores_planejamento.txt` | `Exclusão Lógica do Indicador` == `False` **e** `Exclusão Lógica do Programa` == `False` |

Observação: o formato do indicador de exclusão varia entre bases (texto
`Não`/`Sim` em `programas_planejamento.txt` e `acoes_planejamento.txt`; texto
`False`/`True` em `localizadores_todos_planejamento.txt` e
`indicadores_planejamento.txt`). As funções de carregamento tratam cada base
de acordo com seu próprio formato.

## 2. Fonte dos cards "Previsão 2027 - Orçamento Fiscal / Investimentos"

O documento `prompt_informacoes_elaboracao_painel.txt` não especificava a base
de origem desses dois cards. Como premissa, foram usadas as bases QDD
(Quadro de Detalhamento da Despesa), filtradas por `ANO == 2027`:

- Orçamento Fiscal: soma de `VALOR FINAL (R$)` em `data/BASE_QDD_FISCAL.xlsx`.
- Orçamento de Investimentos: soma de `VALOR (R$)` em
  `data/BASE_QDD_INVESTIMENTO.xlsx`.

Essa escolha foi validada comparando o total com as bases
`BASE_ORCAM_DESPESA_ITEM_FISCAL.xlsx` e `BASE_ORCAM_DESPESA_INVESTIMENTO.xlsx`,
que chegam exatamente ao mesmo valor somado (R$ 153.868.051.650 fiscal e
R$ 9.290.788.295 investimento).

## 3. Página Despesa Fiscal: fonte do card e chave do cruzamento com auxiliar_poder

O documento pedia o card "Despesa Total" com `Fonte de dados` apontando para
`BASE_ORCAM_RECEITA_FISCAL.xlsx` (claramente um resquício de copiar/colar da
página de Receita Fiscal, já que o campo "Dado" do mesmo card e o nome do
card ambos se referem a despesa). Foi usada a base indicada no campo "Dado":
soma de `VALOR FINAL (R$)` em `data/BASE_QDD_FISCAL.xlsx` — o mesmo valor do
card "Previsão 2027 - Orçamento Fiscal" da Visão Geral (R$ 153,8 bi), o que
faz sentido: é a mesma despesa fiscal vista por duas páginas diferentes.

Para o gráfico "Despesa por Poder e Reserva de Contingência", o documento
pedia cruzar `COD_ORGAO` de `BASE_QDD_FISCAL.xlsx` com `uo_cod` de
`auxiliar_poder.csv`. Esse cruzamento deixa 33 códigos de `COD_ORGAO` sem
correspondência. `COD_UO` (não `COD_ORGAO`) é a coluna que corresponde a
`uo_cod` sem nenhuma lacuna — faz sentido, já que `auxiliar_poder.csv` é uma
tabela de Unidades Orçamentárias (coluna `uo_cod`), não de Órgãos. O
cruzamento foi feito por `COD_UO`.
