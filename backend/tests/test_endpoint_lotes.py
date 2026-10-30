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