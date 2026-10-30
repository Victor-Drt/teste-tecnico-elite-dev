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