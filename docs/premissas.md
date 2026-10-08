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
