# Banco de dados

O sistema usa **PostgreSQL**. Cada integrante tem um servidor PostgreSQL no próprio computador, com um banco e um usuário só para o projeto. Este guia é feito uma única vez por pessoa.

## 1. Instale o PostgreSQL

### Linux (Ubuntu, Debian) e WSL

```bash
sudo apt update
sudo apt install postgresql
```

O servidor já fica ligado depois da instalação. No WSL, se ele não ligar sozinho, rode `sudo service postgresql start`.

### Windows

1. Baixe o instalador em <https://www.postgresql.org/download/windows/>.
2. Avance com as opções padrão. Quando o instalador pedir uma senha para o usuário `postgres`, escolha uma e **anote**.
3. Mantenha a porta `5432`.
4. No fim, desmarque o "Stack Builder". Ele não é necessário.

### macOS

```bash
brew install postgresql@16
brew services start postgresql@16
```

## 2. Abra o terminal do PostgreSQL como administrador

| Sistema | Como abrir |
| --- | --- |
| Linux e WSL | `sudo -u postgres psql` |
| Windows | Menu Iniciar → **SQL Shell (psql)**. Pressione Enter em Server, Database, Port e Username, e digite a senha anotada na instalação |
| macOS | `psql postgres` |

Quando funciona, a linha do terminal passa a começar com `postgres=#`.

## 3. Crie o usuário e o banco do projeto

Digite os dois comandos abaixo, um de cada vez. O ponto e vírgula no final é obrigatório.

```sql
CREATE USER paes WITH PASSWORD 'paes123' CREATEDB;
CREATE DATABASE sistema_paes OWNER paes;
```

As respostas esperadas são `CREATE ROLE` e `CREATE DATABASE`. Para sair, digite `\q`.

A permissão `CREATEDB` é necessária para os testes automáticos: o comando `python manage.py test` cria um banco temporário chamado `test_sistema_paes` e o apaga no final.

## 4. Crie o arquivo `.env`

Na raiz do projeto, copie o modelo:

```bash
cp .env.example .env            # Linux, macOS, WSL e Git Bash
copy .env.example .env          # Prompt de Comando do Windows
```

Se você usou o usuário, a senha e o nome de banco do passo 3, não precisa alterar nada. O arquivo `.env` fica só no seu computador e não vai para o GitHub.

| Variável | Significado | Valor padrão |
| --- | --- | --- |
| `DB_NAME` | Nome do banco | `sistema_paes` |
| `DB_USER` | Usuário do banco | `paes` |
| `DB_PASSWORD` | Senha do usuário | `paes123` |
| `DB_HOST` | Endereço do servidor | `localhost` |
| `DB_PORT` | Porta do servidor | `5432` |

## 5. Instale as dependências e crie as tabelas

Com o ambiente virtual ativo:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

O `createsuperuser` é necessário de novo porque o banco é novo e está vazio.

## 6. Confira

```bash
python manage.py test
python manage.py runserver
```

Os testes devem terminar em `OK`, e `http://127.0.0.1:8000/` deve abrir a tela de login.

## Problemas comuns

| Mensagem | Causa | Solução |
| --- | --- | --- |
| `No module named 'psycopg'` ou `'dotenv'` | As dependências novas não foram instaladas | Ative o `venv` e rode `pip install -r requirements.txt` |
| `fe_sendauth: no password supplied` | O arquivo `.env` não existe | Faça o passo 4 |
| `password authentication failed for user "paes"` | A senha do `.env` é diferente da criada no passo 3 | Corrija `DB_PASSWORD` no `.env` |
| `database "sistema_paes" does not exist` | O banco não foi criado | Faça o passo 3 |
| `Connection refused` | O servidor PostgreSQL está desligado | Linux e WSL: `sudo service postgresql start`. Windows: inicie o serviço "postgresql" em Serviços |
| `permission denied to create database` ao rodar os testes | O usuário foi criado sem `CREATEDB` | No `psql` como administrador: `ALTER USER paes CREATEDB;` |
| `relation "..." does not exist` | As migrations não foram aplicadas | `python manage.py migrate` |

## Por que as senhas estão em um arquivo separado

Os dados de conexão ficam no `.env`, e não no `settings.py`, para que nenhuma senha vá para o repositório. O `.env.example` mostra quais variáveis existem, sem ser usado pelo sistema. A senha `paes123` é apenas para desenvolvimento local.
