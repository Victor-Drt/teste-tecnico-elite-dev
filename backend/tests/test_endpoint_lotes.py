import pytest

from app.models.lotes import Lote


@pytest.mark.lotes
def test_deve_cadastrar_lote_com_sucesso_para_leiloeiro(
    client, cabecalho_autenticado, itens_catalogo_teste, db_session
):
    item = itens_catalogo_teste[0]
    payload = {
        "item_id": item.id,
        "data_inicio": "2030-01-01T10:00:00",
        "data_fim": "2030-01-01T12:00:00",
        "valor_minimo": 100.00,
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
    assert response.json()["valor_minimo"] == "100.00"
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
        "valor_minimo": 100.00,
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
        "valor_minimo": 100.00,
        "incremento_minimo": 10.00,
    }

    response = client.post(
        "/api/v1/lotes/",
        json=payload,
        headers=cabecalho_licitante,
    )

    assert response.status_code == 401
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
            "status": lote_teste.status.value,
            "vencedor_id": lote_teste.vencedor_id,
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
def test_deve_retornar_401_quando_usuario_nao_tiver_permissao_para_listar_lotes(
    client, cabecalho_licitante
):
    response = client.get(
        "/api/v1/lotes/",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 401
    assert "detail" in response.json()


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
    assert response.json()["valor_minimo"] == "100.00"
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

    assert response.status_code == 401
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
        "valor_minimo": 200.00,
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

    db_session.refresh(lote_teste)
    assert lote_teste.item_id == item_atualizado.id
    assert lote_teste.valor_minimo == 200.00
    assert lote_teste.incremento_minimo == 20.00


@pytest.mark.lotes
def test_deve_retornar_404_quando_lote_a_atualizar_nao_existir(
    client, cabecalho_autenticado, itens_catalogo_teste
):
    payload = {
        "item_id": itens_catalogo_teste[0].id,
        "data_inicio": "2031-02-01T10:00:00",
        "data_fim": "2031-02-01T12:00:00",
        "valor_minimo": 200.00,
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
        "valor_minimo": 200.00,
        "incremento_minimo": 20.00,
    }

    response = client.patch(
        f"/api/v1/lotes/{lote_teste.id}",
        json=payload,
        headers=cabecalho_licitante,
    )

    assert response.status_code == 401
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
        valor_minimo=200,
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

    assert response.status_code == 401
    assert "detail" in response.json()
    assert db_session.query(Lote).count() == 1