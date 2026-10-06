# Páginas e rotas

Referência das rotas do sistema. Ao implementar um módulo, siga os caminhos e os nomes desta página e atualize a coluna **Situação**.

- **Rota**: caminho digitado no navegador.
- **Nome**: valor do `name=` no `urls.py`, usado em `{% url 'nome' %}` nos templates e em `reverse('nome')` no código.
- **Situação**: `Feito` ou a sprint em que a rota está planejada.

Todas as rotas, exceto `/login/`, exigem usuário autenticado.

## Acesso e visão geral (app `core`)

| Rota | Nome | Página | Situação |
| --- | --- | --- | --- |
| `/` | `dashboard` | Dashboard com atalhos para os módulos | Sprint 1 |
| `/login/` | `login` | Formulário de acesso do gerente | Sprint 1 |
| `/logout/` | `logout` | Encerra a sessão (somente POST) | Sprint 1 |
| `/admin/` | — | Painel administrativo do Django | Sprint 1 |

## Padrão dos cadastros

Unidades, clientes, fornecedores e funcionários seguem o mesmo padrão de quatro rotas.

| Rota | Nome | Página | View genérica |
| --- | --- | --- | --- |
| `/<modulo>/` | `<modulo>_lista` | Listagem com busca e paginação | `ListView` |
| `/<modulo>/novo/` | `<modulo>_criar` | Formulário de cadastro | `CreateView` |
| `/<modulo>/<id>/editar/` | `<modulo>_editar` | Formulário de edição | `UpdateView` |
| `/<modulo>/<id>/excluir/` | `<modulo>_excluir` | Confirmação de exclusão | `DeleteView` |

## Unidades (app `unidades`)

| Rota | Nome | Situação |
| --- | --- | --- |
| `/unidades/` | `unidades_lista` | Sprint 2 |
| `/unidades/novo/` | `unidades_criar` | Sprint 2 |
| `/unidades/<id>/editar/` | `unidades_editar` | Sprint 2 |
| `/unidades/<id>/excluir/` | `unidades_excluir` | Sprint 2 |

## Clientes (app `clientes`)

| Rota | Nome | Situação |
| --- | --- | --- |
| `/clientes/` | `clientes_lista` | Sprint 2 |
| `/clientes/novo/` | `clientes_criar` | Sprint 2 |
| `/clientes/<id>/editar/` | `clientes_editar` | Sprint 2 |
| `/clientes/<id>/excluir/` | `clientes_excluir` | Sprint 2 |

## Fornecedores (app `fornecedores`)

| Rota | Nome | Situação |
| --- | --- | --- |
| `/fornecedores/` | `fornecedores_lista` | Sprint 3 |
| `/fornecedores/novo/` | `fornecedores_criar` | Sprint 3 |
| `/fornecedores/<id>/editar/` | `fornecedores_editar` | Sprint 3 |
| `/fornecedores/<id>/excluir/` | `fornecedores_excluir` | Sprint 3 |

## Funcionários (app `funcionarios`)

| Rota | Nome | Situação |
| --- | --- | --- |
| `/funcionarios/` | `funcionarios_lista` | Sprint 3 |
| `/funcionarios/novo/` | `funcionarios_criar` | Sprint 3 |
| `/funcionarios/<id>/editar/` | `funcionarios_editar` | Sprint 3 |
| `/funcionarios/<id>/excluir/` | `funcionarios_excluir` | Sprint 3 |

## Estoque (app `estoque`)

| Rota | Nome | Página | Situação |
| --- | --- | --- | --- |
| `/estoque/` | `estoque_lista` | Itens em estoque, com alerta de estoque baixo | Sprint 4 |
| `/estoque/novo/` | `estoque_criar` | Cadastro de produto ou insumo | Sprint 4 |
| `/estoque/<id>/editar/` | `estoque_editar` | Edição de item | Sprint 4 |
| `/estoque/<id>/excluir/` | `estoque_excluir` | Confirmação de exclusão | Sprint 4 |
| `/estoque/<id>/movimentar/` | `estoque_movimentar` | Registro de entrada ou saída | Sprint 4 |
| `/estoque/movimentacoes/` | `estoque_movimentacoes` | Histórico de movimentações | Sprint 4 |

## Faturamento (app `faturamento`)

| Rota | Nome | Página | Situação |
| --- | --- | --- | --- |
| `/faturamento/` | `faturamento_lista` | Lançamentos, com filtro por unidade e período | Sprint 5 |
| `/faturamento/novo/` | `faturamento_criar` | Novo lançamento | Sprint 5 |
| `/faturamento/<id>/editar/` | `faturamento_editar` | Edição de lançamento | Sprint 5 |
| `/faturamento/<id>/excluir/` | `faturamento_excluir` | Confirmação de exclusão | Sprint 5 |

## Manutenção (app `manutencao`)

| Rota | Nome | Página | Situação |
| --- | --- | --- | --- |
| `/manutencao/` | `manutencao_lista` | Manutenções, com filtro por equipamento e status | Sprint 5 |
| `/manutencao/nova/` | `manutencao_criar` | Nova manutenção | Sprint 5 |
| `/manutencao/<id>/editar/` | `manutencao_editar` | Edição de manutenção | Sprint 5 |
| `/manutencao/<id>/excluir/` | `manutencao_excluir` | Confirmação de exclusão | Sprint 5 |
| `/manutencao/equipamentos/` | `equipamentos_lista` | Equipamentos cadastrados | Sprint 5 |
| `/manutencao/equipamentos/novo/` | `equipamentos_criar` | Cadastro de equipamento | Sprint 5 |
| `/manutencao/equipamentos/<id>/editar/` | `equipamentos_editar` | Edição de equipamento | Sprint 5 |
| `/manutencao/equipamentos/<id>/excluir/` | `equipamentos_excluir` | Confirmação de exclusão | Sprint 5 |
