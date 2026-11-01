import asyncio
from decimal import Decimal

import pytest
from starlette.websockets import WebSocketDisconnect

from app.models.lances import Lance
from app.models.lotes import StatusLote
from app.websockets.manage import ConnectionManager


@pytest.mark.lances
def test_connection_manager_transmite_apenas_para_o_lote_conectado():
    class FakeWebSocket:
        def __init__(self):
            self.messages = []

        async def accept(self):
            pass

        async def send_json(self, message):
            self.messages.append(message)

    async def verify_rooms():
        manager = ConnectionManager()
        websocket_a = FakeWebSocket()
        websocket_b = FakeWebSocket()
        message = {"tipo": "lance_atualizado"}

        await manager.connect(1, websocket_a)
        await manager.connect(2, websocket_b)
        await manager.broadcast(1, message)

        assert websocket_a.messages == [message]
        assert websocket_b.messages == []

        manager.disconnect(1, websocket_a)
        assert 1 not in manager.active_connections
        assert manager.active_connections[2] == {websocket_b}

    asyncio.run(verify_rooms())


@pytest.mark.lances
def test_sala_websocket_entrega_estado_inicial_do_lote(
    client,
    cabecalho_licitante,
    lote_ao_vivo,
    usuario_licitante,
    outro_usuario_licitante,
    db_session,
):
    lance_anterior = Lance(
        licitante_id=usuario_licitante.id,
        lote_id=lote_ao_vivo.id,
        valor=120,
    )
    lance_atual = Lance(
        licitante_id=outro_usuario_licitante.id,
        lote_id=lote_ao_vivo.id,
        valor=140,
    )
    lote_ao_vivo.valor_atual = Decimal("140.00")
    db_session.add_all([lance_anterior, lance_atual])
    db_session.commit()
    lote_id = lote_ao_vivo.id
    data_fim = lote_ao_vivo.data_fim.isoformat()
    lance_anterior_id = lance_anterior.id
    lance_atual_id = lance_atual.id
    usuario_id = usuario_licitante.id
    outro_usuario_id = outro_usuario_licitante.id

    with client.websocket_connect(
        f"/api/v1/ws/leilao/{lote_id}",
        headers=cabecalho_licitante,
    ) as websocket:
        evento = websocket.receive_json()

    assert evento["tipo"] == "sala_inicial"
    assert evento["lote"] == {
        "id": lote_id,
        "status": StatusLote.AO_VIVO.value,
        "data_fim": data_fim,
        "valor_atual": "140.00",
    }
    assert evento["lance_atual"]["id"] == lance_atual_id
    assert evento["lance_atual"]["valor"] == "140.00"
    assert [lance["id"] for lance in evento["historico_lances"]] == [
        lance_atual_id,
        lance_anterior_id,
    ]
    assert evento["participantes"] == [
        {
            "licitante_id": outro_usuario_id,
            "posicao": 1,
            "situacao": "ganhando",
        },
        {
            "licitante_id": usuario_id,
            "posicao": 2,
            "situacao": "superado",
        },
    ]
    assert evento["usuario"] == {
        "id": usuario_id,
        "posicao": 2,
        "situacao": "superado",
    }


@pytest.mark.lances
def test_novo_lance_e_transmitido_aos_usuarios_conectados_na_sala(
    client,
    cabecalho_licitante,
    cabecalho_outro_licitante,
    lote_ao_vivo,
    carteira_licitante,
    carteira_outro_licitante,
    usuario_licitante,
    outro_usuario_licitante,
    db_session,
):
    lance_anterior = Lance(
        licitante_id=usuario_licitante.id,
        lote_id=lote_ao_vivo.id,
        valor=120,
    )
    lote_ao_vivo.valor_atual = Decimal("120.00")
    carteira_licitante.saldo_comprometido = Decimal("120.00")
    db_session.add(lance_anterior)
    db_session.commit()
    lote_id = lote_ao_vivo.id
    usuario_id = usuario_licitante.id
    outro_usuario_id = outro_usuario_licitante.id

    with (
        client.websocket_connect(
            f"/api/v1/ws/leilao/{lote_id}",
            headers=cabecalho_licitante,
        ) as websocket_licitante,
        client.websocket_connect(
            f"/api/v1/ws/leilao/{lote_id}",
            headers=cabecalho_outro_licitante,
        ) as websocket_outro,
    ):
        estado_licitante = websocket_licitante.receive_json()
        estado_outro = websocket_outro.receive_json()
        assert estado_licitante["usuario"]["situacao"] == "ganhando"
        assert estado_outro["usuario"]["situacao"] == "sem_lance"

        response = client.post(
            "/api/v1/lances/",
            json={"lote_id": lote_id, "valor": 131},
            headers=cabecalho_outro_licitante,
        )
        assert response.status_code == 201

        evento_licitante = websocket_licitante.receive_json()
        evento_outro = websocket_outro.receive_json()

    for evento in (evento_licitante, evento_outro):
        assert evento["tipo"] == "lance_atualizado"
        assert evento["lote_id"] == lote_id
        assert evento["lance"]["licitante_id"] == outro_usuario_id
        assert evento["lance"]["valor"] == "131.00"
        assert evento["lance_atual"]["valor"] == "131.00"
        assert evento["valor_atual"] == "131.00"
        assert evento["participantes"] == [
            {
                "licitante_id": outro_usuario_id,
                "posicao": 1,
                "situacao": "ganhando",
            },
            {
                "licitante_id": usuario_id,
                "posicao": 2,
                "situacao": "superado",
            },
        ]


@pytest.mark.lances
def test_sala_websocket_exige_autenticacao(client, lote_ao_vivo):
    with pytest.raises(WebSocketDisconnect) as desconexao:
        with client.websocket_connect(f"/api/v1/ws/leilao/{lote_ao_vivo.id}"):
            pass

    assert desconexao.value.code == 1008


@pytest.mark.lances
def test_sala_websocket_rejeita_lote_que_nao_esteja_ao_vivo(
    client,
    cabecalho_licitante,
    lote_teste,
):
    with pytest.raises(WebSocketDisconnect) as desconexao:
        with client.websocket_connect(
            f"/api/v1/ws/leilao/{lote_teste.id}",
            headers=cabecalho_licitante,
        ):
            pass

    assert desconexao.value.code == 1008
