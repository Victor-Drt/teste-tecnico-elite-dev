# Teste Tecnico Elite Dev / Casa de Leilões

Projeto desenvolvido como parte do teste técnico para o processo seletivo da Elite Dev - Verzel.

## 🛠️ Tecnologias Principais
* Frontend: React
* Backend: FastAPI (Python)

> ⚠️ *Status: Em desenvolvimento.*

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