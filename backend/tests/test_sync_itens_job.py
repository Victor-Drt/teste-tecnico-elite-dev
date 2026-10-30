import asyncio
import logging

import pytest

from app.jobs import sync_itens


@pytest.mark.itens
def test_deve_registrar_falha_sem_interromper_ciclo_de_sincronizacao(
    monkeypatch, caplog
):
    async def falhar_sincronizacao():
        raise RuntimeError("API externa indisponível")

    monkeypatch.setattr(sync_itens, "sincronizar_uma_vez", falhar_sincronizacao)

    with caplog.at_level(logging.ERROR):
        asyncio.run(sync_itens.executar_ciclo())

    assert "Falha ao sincronizar itens" in caplog.text
    assert "API externa indisponível" in caplog.text
