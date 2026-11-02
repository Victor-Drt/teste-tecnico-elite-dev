import pytest

from app.models.lances import Lance
from app.models.lotes import Lote, StatusLote


@pytest.mark.lotes
def test_deve_cadastrar_lote_com_sucesso_para_leiloeiro(
    client, cabecalho_autenticado, itens_catalogo_teste, db_session
):
    item = itens_catalogo_teste[0]
    payload = {
        "item_id": item.id,
        "data_inicio": "2030-01-01T10:00:00",
        "data_fim": "2030-01-01T12:00:00",
        "valor_inicial": 100.00,
        "incremento_minimo": 10.00,
    }

    response = client.post(
        "/api/v1/lotes/",
        json=payload,
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 201
    assert response.json()["item_id"] == item.id
    assert response.json()["leiloeiro_id"] > 0
    assert response.json()["valor_inicial"] == "100.00"
    assert response.json()["valor_atual"] == "100.00"
    assert db_session.query(Lote).one().valor_atual == 100.00
    assert response.json()["incremento_minimo"] == "10.00"
    assert response.json()["status"] == "em_breve"

    lote_salvo = db_session.query(Lote).one()
    assert lote_salvo.item_id == item.id
    assert lote_salvo.leiloeiro_id == response.json()["leiloeiro_id"]


@pytest.mark.lotes
def test_deve_retornar_401_ao_cadastrar_lote_sem_autenticacao(
    client, itens_catalogo_teste
):
    payload = {
        "item_id": itens_catalogo_teste[0].id,
        "data_inicio": "2030-01-01T10:00:00",
        "data_fim": "2030-01-01T12:00:00",
        "valor_inicial": 100.00,
        "incremento_minimo": 10.00,
    }

    response = client.post("/api/v1/lotes/", json=payload)

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.lotes
def test_deve_retornar_401_quando_usuario_nao_for_leiloeiro(
    client, cabecalho_licitante, itens_catalogo_teste, db_session
):
    payload = {
        "item_id": itens_catalogo_teste[0].id,
        "data_inicio": "2030-01-01T10:00:00",
        "data_fim": "2030-01-01T12:00:00",
        "valor_inicial": 100.00,
        "incremento_minimo": 10.00,
    }

    response = client.post(
        "/api/v1/lotes/",
        json=payload,
        headers=cabecalho_licitante,
    )

    assert response.status_code == 403
    assert "detail" in response.json()
    assert db_session.query(Lote).count() == 0


@pytest.mark.lotes
def test_deve_retornar_resumos_dos_lotes_quando_leiloeiro_autorizado(
    client, cabecalho_autenticado, lote_teste
):
    response = client.get(
        "/api/v1/lotes/",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": lote_teste.id,
            "item_id": lote_teste.item_id,
            "data_inicio": lote_teste.data_inicio.isoformat(),
            "data_fim": lote_teste.data_fim.isoformat(),
            "valor_atual": "100.00",
            "status": lote_teste.status.value,
            "vencedor_id": lote_teste.vencedor_id,
            "item": {
                "id": lote_teste.item.id,
                "titulo": lote_teste.item.titulo,
                "data_exibicao": lote_teste.item.data_exibicao,
                "info_artista": lote_teste.item.info_artista,
                "imagem_id": lote_teste.item.imagem_id,
                "imagem_url": (
                    "https://www.artic.edu/iiif/2/img-123/full/843,/0/default.jpg"
                ),
            },
        }
    ]


@pytest.mark.lotes
def test_deve_retornar_lista_vazia_quando_leiloeiro_nao_tiver_lotes(
    client, cabecalho_autenticado
):
    response = client.get(
        "/api/v1/lotes/",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.lotes
def test_licitante_deve_listar_lotes_publicos(
    client, cabecalho_licitante, lote_teste
):
    response = client.get(
        "/api/v1/lotes/",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    assert [lote["id"] for lote in response.json()] == [lote_teste.id]
    assert response.json()[0]["valor_atual"] == "100.00"


@pytest.mark.lotes
def test_licitante_nao_deve_listar_lotes_cancelados(
    client, cabecalho_licitante, lote_teste, db_session
):
    lote_teste.status = StatusLote.CANCELADO
    db_session.commit()

    response = client.get(
        "/api/v1/lotes/",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.lotes
def test_licitante_deve_obter_detalhes_do_lote_para_vitrine(
    client, cabecalho_licitante, lote_teste
):
    response = client.get(
        f"/api/v1/lotes/{lote_teste.id}/vitrine",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    assert response.json()["id"] == lote_teste.id
    assert response.json()["incremento_minimo"] == "10.00"
    assert response.json()["item"] == {
        "id": lote_teste.item.id,
        "titulo": lote_teste.item.titulo,
        "data_exibicao": lote_teste.item.data_exibicao,
        "info_artista": lote_teste.item.info_artista,
        "imagem_id": lote_teste.item.imagem_id,
        "imagem_url": (
            "https://www.artic.edu/iiif/2/img-123/full/843,/0/default.jpg"
        ),
        "descricao": lote_teste.item.descricao,
    }


@pytest.mark.lotes
def test_vitrine_nao_deve_retornar_lote_cancelado(
    client, cabecalho_licitante, lote_teste, db_session
):
    lote_teste.status = StatusLote.CANCELADO
    db_session.commit()

    response = client.get(
        f"/api/v1/lotes/{lote_teste.id}/vitrine",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 404


@pytest.mark.lotes
def test_deve_filtrar_lotes_por_status(
    client, cabecalho_licitante, lote_teste, db_session
):
    lote_teste.status = StatusLote.AO_VIVO
    db_session.commit()

    response = client.get(
        "/api/v1/lotes/?status=ao_vivo",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    assert [lote["id"] for lote in response.json()] == [lote_teste.id]


@pytest.mark.lotes
def test_deve_rejeitar_limite_de_lotes_acima_do_maximo(
    client, cabecalho_licitante
):
    response = client.get(
        "/api/v1/lotes/?limit=101",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 422


@pytest.mark.lotes
def test_deve_retornar_detalhes_do_lote_quando_leiloeiro_autorizado(
    client, cabecalho_autenticado, lote_teste
):
    response = client.get(
        f"/api/v1/lotes/{lote_teste.id}",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 200
    assert response.json()["id"] == lote_teste.id
    assert response.json()["item_id"] == lote_teste.item_id
    assert response.json()["leiloeiro_id"] == lote_teste.leiloeiro_id
    assert response.json()["valor_inicial"] == "100.00"
    assert response.json()["valor_atual"] == "100.00"
    assert response.json()["incremento_minimo"] == "10.00"
    assert response.json()["status"] == "em_breve"


@pytest.mark.lotes
def test_deve_retornar_404_quando_lote_nao_existir(
    client, cabecalho_autenticado
):
    response = client.get(
        "/api/v1/lotes/99999",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lote não encontrado"


@pytest.mark.lotes
def test_deve_retornar_401_quando_usuario_nao_tiver_permissao_para_lote(
    client, cabecalho_licitante, lote_teste
):
    response = client.get(
        f"/api/v1/lotes/{lote_teste.id}",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 403
    assert "detail" in response.json()


@pytest.mark.lotes
def test_deve_atualizar_lote_quando_leiloeiro_tiver_permissao(
    client, cabecalho_autenticado, lote_teste, itens_catalogo_teste, db_session
):
    item_atualizado = itens_catalogo_teste[1]
    payload = {
        "item_id": item_atualizado.id,
        "data_inicio": "2031-02-01T10:00:00",
        "data_fim": "2031-02-01T12:00:00",
        "valor_inicial": 200.00,
        "incremento_minimo": 20.00,
    }

    response = client.patch(
        f"/api/v1/lotes/{lote_teste.id}",
        json=payload,
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 200
    assert response.json()["id"] == lote_teste.id
    assert response.json()["item_id"] == item_atualizado.id
    assert response.json()["data_inicio"] == "2031-02-01T10:00:00"
    assert response.json()["data_fim"] == "2031-02-01T12:00:00"
    assert response.json()["valor_atual"] == "100.00"

    db_session.refresh(lote_teste)
    assert lote_teste.item_id == item_atualizado.id
    assert lote_teste.valor_inicial == 200.00
    assert lote_teste.valor_atual == 100.00
    assert lote_teste.incremento_minimo == 20.00


@pytest.mark.lotes
def test_nao_deve_cancelar_lote_que_ja_recebeu_lances(
    client,
    cabecalho_autenticado,
    lote_teste,
    usuario_licitante,
    db_session,
):
    db_session.add(
        Lance(
            licitante_id=usuario_licitante.id,
            lote_id=lote_teste.id,
            valor=120,
        )
    )
    db_session.commit()

    response = client.patch(
        f"/api/v1/lotes/{lote_teste.id}",
        json={"status": "cancelado"},
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 409
    assert "já recebeu lances" in response.json()["detail"]
    db_session.refresh(lote_teste)
    assert lote_teste.status != StatusLote.CANCELADO


@pytest.mark.lotes
def test_deve_cancelar_lote_sem_lances(
    client, cabecalho_autenticado, lote_teste, db_session
):
    response = client.patch(
        f"/api/v1/lotes/{lote_teste.id}",
        json={"status": "cancelado"},
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 200
    db_session.refresh(lote_teste)
    assert lote_teste.status == StatusLote.CANCELADO


@pytest.mark.lotes
def test_deve_retornar_404_quando_lote_a_atualizar_nao_existir(
    client, cabecalho_autenticado, itens_catalogo_teste
):
    payload = {
        "item_id": itens_catalogo_teste[0].id,
        "data_inicio": "2031-02-01T10:00:00",
        "data_fim": "2031-02-01T12:00:00",
        "valor_inicial": 200.00,
        "incremento_minimo": 20.00,
    }

    response = client.patch(
        "/api/v1/lotes/99999",
        json=payload,
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lote não encontrado"


@pytest.mark.lotes
def test_deve_retornar_401_quando_usuario_nao_tiver_permissao_para_atualizar_lote(
    client, cabecalho_licitante, lote_teste, itens_catalogo_teste
):
    payload = {
        "item_id": itens_catalogo_teste[0].id,
        "data_inicio": "2031-02-01T10:00:00",
        "data_fim": "2031-02-01T12:00:00",
        "valor_inicial": 200.00,
        "incremento_minimo": 20.00,
    }

    response = client.patch(
        f"/api/v1/lotes/{lote_teste.id}",
        json=payload,
        headers=cabecalho_licitante,
    )

    assert response.status_code == 403
    assert "detail" in response.json()


@pytest.mark.lotes
def test_deve_deletar_lote_quando_leiloeiro_tiver_permissao(
    client,
    cabecalho_autenticado,
    lote_teste,
    usuario_licitante,
    itens_catalogo_teste,
    db_session,
):
    from datetime import datetime

    leiloeiro_id = lote_teste.leiloeiro_id
    lote_teste.leiloeiro_id = usuario_licitante.id
    lote_alvo = Lote(
        item_id=itens_catalogo_teste[1].id,
        leiloeiro_id=leiloeiro_id,
        valor_inicial=200,
        valor_atual=200,
        incremento_minimo=20,
        data_inicio=datetime(2031, 2, 1, 10),
        data_fim=datetime(2031, 2, 1, 12),
    )
    db_session.add(lote_alvo)
    db_session.commit()
    db_session.refresh(lote_alvo)

    response = client.delete(
        f"/api/v1/lotes/{lote_alvo.id}",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 204
    assert response.content == b""
    assert db_session.query(Lote).filter_by(id=lote_alvo.id).one_or_none() is None
    assert db_session.query(Lote).filter_by(id=lote_teste.id).one_or_none() is not None


@pytest.mark.lotes
def test_nao_deve_deletar_lote_ao_vivo(
    client, cabecalho_autenticado, lote_ao_vivo, db_session
):
    response = client.delete(
        f"/api/v1/lotes/{lote_ao_vivo.id}",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 409
    assert "ao vivo" in response.json()["detail"]
    assert db_session.query(Lote).filter_by(id=lote_ao_vivo.id).one_or_none() is not None


@pytest.mark.lotes
def test_nao_deve_deletar_lote_que_ja_recebeu_lances(
    client,
    cabecalho_autenticado,
    lote_teste,
    usuario_licitante,
    db_session,
):
    db_session.add(
        Lance(
            licitante_id=usuario_licitante.id,
            lote_id=lote_teste.id,
            valor=120,
        )
    )
    db_session.commit()

    response = client.delete(
        f"/api/v1/lotes/{lote_teste.id}",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 409
    assert "já recebeu lances" in response.json()["detail"]
    assert db_session.query(Lote).filter_by(id=lote_teste.id).one_or_none() is not None


@pytest.mark.lotes
def test_deve_retornar_404_quando_lote_a_deletar_nao_existir(
    client, cabecalho_autenticado
):
    response = client.delete(
        "/api/v1/lotes/99999",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lote não encontrado"


@pytest.mark.lotes
def test_deve_retornar_401_quando_usuario_nao_tiver_permissao_para_deletar_lote(
    client, cabecalho_licitante, lote_teste, db_session
):
    response = client.delete(
        f"/api/v1/lotes/{lote_teste.id}",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 403
    assert "detail" in response.json()
    assert db_session.query(Lote).count() == 1


@pytest.mark.lotes
def test_deve_listar_arremates_concluidos_do_usuario_autenticado(
    client,
    cabecalho_licitante,
    lote_teste,
    usuario_licitante,
    usuario_teste,
    itens_catalogo_teste,
    db_session,
):
    from datetime import datetime

    lote_teste.status = StatusLote.CONCLUIDO
    lote_teste.vencedor_id = usuario_licitante.id

    lote_em_andamento = Lote(
        item_id=itens_catalogo_teste[1].id,
        leiloeiro_id=usuario_teste.id,
        valor_inicial=200,
        valor_atual=250,
        incremento_minimo=10,
        status=StatusLote.AO_VIVO,
        data_inicio=datetime(2031, 1, 1, 10),
        data_fim=datetime(2031, 1, 1, 12),
    )
    lote_de_outro_vencedor = Lote(
        item_id=itens_catalogo_teste[2].id,
        leiloeiro_id=usuario_teste.id,
        valor_inicial=300,
        valor_atual=350,
        incremento_minimo=10,
        status=StatusLote.CONCLUIDO,
        vencedor_id=usuario_teste.id,
        data_inicio=datetime(2032, 1, 1, 10),
        data_fim=datetime(2032, 1, 1, 12),
    )
    db_session.add_all([lote_em_andamento, lote_de_outro_vencedor])
    db_session.commit()

    response = client.get(
        "/api/v1/lotes/arremates",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": lote_teste.id,
            "item_id": lote_teste.item_id,
            "data_inicio": lote_teste.data_inicio.isoformat(),
            "data_fim": lote_teste.data_fim.isoformat(),
            "valor_atual": "100.00",
            "status": StatusLote.CONCLUIDO.value,
            "vencedor_id": usuario_licitante.id,
        }
    ]


@pytest.mark.lotes
def test_deve_retornar_lista_vazia_quando_usuario_nao_tiver_arremates(
    client, cabecalho_licitante
):
    response = client.get(
        "/api/v1/lotes/arremates",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.lotes
def test_deve_retornar_401_ao_listar_arremates_sem_autenticacao(client):
    response = client.get("/api/v1/lotes/arremates")

    assert response.status_code == 401
    assert "detail" in response.json()