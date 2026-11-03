# Teste Tecnico Elite Dev / Casa de Leilões

Projeto desenvolvido como parte do teste técnico para o processo seletivo da Elite Dev - Verzel.

## 🛠️ Tecnologias Principais
* Frontend: React
* Backend: FastAPI (Python)

> ⚠️ *Status: Em desenvolvimento.*

## Execução local com Docker

### Pré-requisitos

- Docker Engine instalado e em execução.
- Docker Compose v2 (`docker compose`).

### Configurar e iniciar

O Compose carrega `.env.example` como configuração local padrão; um arquivo
`.env` na raiz é opcional e sobrescreve os valores de exemplo. Para personalizar
as configurações sem alterar o modelo, copie-o na raiz do projeto:

```bash
cp .env.example .env
```

Edite `.env` antes de iniciar. Se não criar esse arquivo, o Compose ainda inicia
com os valores de `.env.example`, adequados apenas para desenvolvimento local:

- Troque `POSTGRES_PASSWORD` e `SECRET_KEY` por valores próprios.
- No Compose, a URL do banco é montada automaticamente com o host `postgres`
  e as credenciais de `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`.
  Não use `localhost` como host do banco dentro dos containers.
- Configure `API_EXTERNA_URL` com a URL da API de itens que será sincronizada.
- Mantenha `VITE_API_URL` apontando para a API acessível pelo navegador, por
  padrão `http://localhost:8000/api/v1`.

Construa as imagens e inicie os serviços a partir da raiz:

```bash
docker compose up --build -d
```

O Compose inicia PostgreSQL, backend e frontend. O backend executa as migrações
do banco antes de iniciar a API. Confira os serviços e acompanhe os logs:

```bash
docker compose ps
docker compose logs -f
```

A aplicação fica disponível em <http://localhost:5173>, a API em
<http://localhost:8000> e a documentação interativa em
<http://localhost:8000/docs>.

O catálogo de itens não é sincronizado automaticamente ao subir os containers.
Depois que o backend estiver em execução, inicie o worker uma única vez:

```bash
docker compose exec -d backend python -m app.jobs.sync_itens
```

Para acompanhar os serviços, use `docker compose logs -f`; para encerrar,
execute `docker compose down`. Os dados do PostgreSQL permanecem no volume
`postgres_data`. **Atenção:** `docker compose down -v` também remove esse volume
e apaga os dados do banco.

## Sincronização dos itens

A aplicação lista os itens a partir do banco local. Para atualizar esse catálogo,
execute o worker de sincronização separadamente do servidor FastAPI, a partir da
pasta `backend`:

```bash
.venv/bin/python -m app.jobs.sync_itens
```

O worker sincroniza as páginas da API externa ao iniciar e repete o processo a
cada 15 minutos. O intervalo pode ser alterado pela variável
`SYNC_ITENS_INTERVAL_SECONDS` (em segundos). Execute apenas uma instância desse
worker por ambiente para evitar sincronizações duplicadas. Se uma sincronização
falhar, o erro é registrado e os itens já salvos permanecem disponíveis.

## Auditoria da cadeia de lances

Cada novo lance recebe um hash SHA-256 calculado sobre seus dados públicos
(pseudônimo do participante, valor, data/hora e identificadores do lance e do
lote), além do hash do evento anterior. O hash final é persistido na liquidação.
A auditoria recalcula a cadeia, compara os hashes dos eventos com a âncora e
exibe o resultado e as provas individuais dos lances.

A migração `c3d4e5f6a7b8` adiciona os campos de hash. Lances e liquidações
anteriores à migração não recebem uma prova retroativa e aparecem como não
verificados. Para registrar alterações de quantidade, a liquidação também
guarda a quantidade de lances no fechamento. A implementação não usa serviços
externos ou armazenamento em nuvem.

**Limitação:** a cadeia detecta alterações quando a âncora permanece intacta,
mas não impede que alguém com acesso suficiente ao banco reescreva os lances,
os hashes e a própria âncora. Como todos esses dados ficam no mesmo banco, não
há proteção contra uma reescrita completa; isso exigiria uma âncora independente,
fora do escopo deste teste técnico.