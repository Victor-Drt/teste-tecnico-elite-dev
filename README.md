# Teste Técnico Elite Dev — Casa de Leilões

Aplicação desenvolvida como parte do processo seletivo Elite Dev da Verzel, contemplando uma plataforma de leilões com gerenciamento de usuários, itens, lotes e auditoria da cadeia de lances.

## 🚀 Acesso à aplicação

**[Acessar Casa de Leilões](https://frontend-production-09b1.up.railway.app)**

- **Documentação da API:** [Swagger UI](https://backend-production-4861.up.railway.app/docs)
- **Protótipo de interface:** [Visualizar no Figma](https://www.figma.com/design/lR8JwF8AGzU76xwuA3vmZ7/EliteDevTesteTecnico?node-id=0-1)

> **Atenção:** A aplicação está hospedada no Railway e pode entrar em modo de suspensão após um período de inatividade. Na primeira tentativa de acesso, pode ser necessário aguardar alguns segundos até que os serviços voltem a responder. Caso a página não carregue imediatamente, aguarde e tente novamente.

## 🔑 Credenciais de demonstração

Foram disponibilizadas três contas para facilitar a avaliação dos diferentes perfis de acesso:

| Perfil | E-mail | Senha |
|---|---|---|
| Licitante 1 | `licitante1@example.com` | `licitante1` |
| Licitante 2 | `licitante2@example.com` | `licitante2` |
| Leiloeiro | `leiloeiro1@example.com` | `leiloeiro1` |

As credenciais são destinadas exclusivamente à avaliação do teste técnico.

## 🛠️ Tecnologias utilizadas

- **Frontend:** React 19, TypeScript e Vite.
- **Backend:** Python e FastAPI.
- **ORM:** SQLAlchemy.
- **Banco de dados:** PostgreSQL.
- **Migrações:** Alembic.
- **Validação de dados:** Pydantic.
- **Infraestrutura:** Docker, Docker Compose e Railway.

## 🐳 Execução local com Docker

### Pré-requisitos

- Docker Engine instalado e em execução.
- Docker Compose v2 (`docker compose`).

### Configuração

O Compose utiliza `.env.example` como configuração padrão. A criação de um arquivo `.env` na raiz do projeto é opcional.

Para personalizar as configurações, copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Edite o `.env` antes de iniciar. Se optar por não criá-lo, o Compose utilizará os valores de `.env.example`, adequados apenas para desenvolvimento local.

Algumas configurações importantes:

- Altere `POSTGRES_PASSWORD` e `SECRET_KEY` para valores próprios.
- A URL do banco utilizada pelos containers é configurada com o host `postgres` e as credenciais definidas em `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`. Não utilize `localhost` como host do banco dentro dos containers.
- Configure `API_EXTERNA_URL` com a URL da API externa utilizada na sincronização dos itens.
- Mantenha `VITE_API_URL` apontando para a API acessível pelo navegador. Por padrão: `http://localhost:8000/api/v1`.

### Inicialização

Na raiz do projeto, execute:

```bash
docker compose up --build -d
```

O Docker Compose inicia os seguintes serviços:

- PostgreSQL;
- Backend FastAPI;
- Frontend React;
- Worker de sincronização de itens (`sync-itens`).

O backend executa as migrações do banco de dados antes de iniciar a API. O worker inicia somente depois que o backend responde ao healthcheck.

Para verificar os serviços:

```bash
docker compose ps
```

Para acompanhar os logs:

```bash
docker compose logs -f
```

Para acompanhar somente o worker:

```bash
docker compose logs -f sync-itens
```

### Endereços locais

| Serviço | Endereço |
|---|---|
| Frontend | http://localhost:5173 |
| Backend / API | http://localhost:8000 |
| Documentação Swagger | http://localhost:8000/docs |

### Encerramento

Para parar os serviços:

```bash
docker compose down
```

Os dados do PostgreSQL permanecem armazenados no volume `postgres_data`.

**Atenção:** o comando `docker compose down -v` também remove o volume e apaga os dados persistidos do banco.

## 🔄 Sincronização dos itens

A aplicação utiliza uma API externa para obter os itens que são armazenados no banco de dados local.

O serviço `sync-itens` executa a primeira sincronização ao iniciar e repete o processo conforme o intervalo definido em `SYNC_ITENS_INTERVAL_SECONDS`, configurado em 900 segundos (15 minutos) por padrão.

A sincronização é executada separadamente do servidor FastAPI, permitindo que o processo de atualização dos itens não bloqueie o atendimento das requisições da API.

**Ambiente de produção:** o worker de sincronização foi temporariamente pausado após a carga inicial dos itens, mantendo os dados já persistidos disponíveis para a avaliação. O serviço permanece configurado no projeto e pode ser iniciado novamente quando necessário.

Para executar o worker manualmente, fora do Docker, a partir da pasta `backend`:

```bash
.venv/bin/python -m app.jobs.sync_itens
```

Mantenha apenas uma instância do worker por ambiente para evitar sincronizações concorrentes.

Em caso de falha, o erro é registrado nos logs e uma nova tentativa ocorre no próximo ciclo. Os itens já persistidos permanecem disponíveis.

## 🔐 Auditoria da cadeia de lances

Cada novo lance recebe um hash SHA-256 calculado a partir de seus dados públicos:

- Pseudônimo do participante;
- Valor do lance;
- Data e hora;
- Identificadores do lance e do lote.

O cálculo também considera o hash do evento anterior, formando uma cadeia de integridade entre os lances.

O hash final é persistido na liquidação. Durante a auditoria, o sistema recalcula a cadeia, compara os hashes dos eventos com a âncora persistida e apresenta o resultado da verificação, incluindo as provas individuais dos lances.

A migração `c3d4e5f6a7b8` adiciona os campos necessários para essa funcionalidade.

Lances e liquidações anteriores à migração não recebem provas retroativas e são apresentados como não verificados.

Para registrar alterações na quantidade de lances, a liquidação também armazena a quantidade de lances existente no momento do fechamento.

### Limitação da implementação

A cadeia permite detectar alterações nos registros quando a âncora permanece intacta. Entretanto, não impede que alguém com acesso suficiente ao banco de dados reescreva os lances, seus hashes e a própria âncora.

Como todos esses dados permanecem no mesmo banco, não existe proteção contra uma reescrita completa da cadeia. Isso exigiria uma âncora independente, armazenada fora do banco principal, o que está fora do escopo deste teste técnico.