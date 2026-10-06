# Guia de contribuição

Este guia descreve como a equipe trabalha no repositório. Vale para todas as sprints.

## Regras gerais

1. Ninguém faz commit direto na `main`. Toda mudança entra por **pull request**.
2. Toda tarefa tem uma **issue**, com responsável, etiqueta e milestone da sprint.
3. Todo pull request precisa da **aprovação de outro integrante** antes do merge.
4. A `main` deve estar sempre funcionando: antes de abrir o pull request, rode `python manage.py check` e `python manage.py test`.

## Fluxo de uma tarefa

```bash
# 1. Atualize a main
git switch main
git pull

# 2. Crie a branch da tarefa
git switch -c feat/nome-da-tarefa

# 3. Trabalhe e faça commits pequenos
git add caminho/do/arquivo
git commit -m "feat: descrição curta do que foi feito"

# 4. Envie a branch para o GitHub
git push -u origin feat/nome-da-tarefa
```

Depois, no GitHub:

1. Abra o pull request da sua branch para a `main`.
2. Na descrição, escreva `Closes #N`, trocando `N` pelo número da issue. Isso fecha a issue automaticamente no merge.
3. Peça a revisão de um colega.
4. Após a aprovação, faça o merge e apague a branch.

Para terminar, na sua máquina:

```bash
git switch main
git pull
git branch -d feat/nome-da-tarefa
```

## Nomes de branch

Formato: `tipo/descricao-curta`, em minúsculas, sem acentos e com hífens.

| Exemplo | Quando usar |
| --- | --- |
| `feat/crud-clientes` | Nova funcionalidade |
| `fix/saida-estoque-negativa` | Correção de erro |
| `docs/rotas-do-sistema` | Documentação |
| `chore/setup-projeto` | Configuração e manutenção |

## Mensagens de commit

Formato: `tipo: descrição no presente, em minúsculas, sem ponto final`.

| Tipo | Uso | Exemplo |
| --- | --- | --- |
| `feat` | Nova funcionalidade | `feat: adiciona listagem de fornecedores` |
| `fix` | Correção de erro | `fix: bloqueia saída maior que o estoque` |
| `docs` | Documentação | `docs: documenta rotas do módulo de estoque` |
| `style` | Ajuste visual ou de formatação, sem mudar comportamento | `style: ajusta espaçamento do menu` |
| `refactor` | Reorganização de código, sem mudar comportamento | `refactor: extrai formulário de cliente` |
| `test` | Testes | `test: adiciona testes do login` |
| `chore` | Configuração e dependências | `chore: atualiza requirements.txt` |

## Revisão de pull request

Quem revisa deve:

1. Baixar a branch e rodar o projeto localmente.
2. Conferir os itens da lista de verificação do pull request.
3. Aprovar em **Files changed → Review changes → Approve**, ou comentar o que precisa mudar.

```bash
git fetch
git switch nome-da-branch
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Padrões de código

- Nomes de apps, models, campos, rotas e templates em **português**, sem acentos no código (`funcionarios`, `manutencao`).
- Um app Django por módulo do sistema.
- Rotas no padrão descrito em [`docs/rotas.md`](docs/rotas.md).
- Toda página interna estende `templates/base.html` e exige login (`LoginRequiredMixin`).
- Ao alterar um model, gere a migration (`python manage.py makemigrations`) e inclua o arquivo no commit.
