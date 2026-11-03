from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.models.lances import Lance
from app.models.lotes import StatusLote
from app.core.time import utc_now_naive


@pytest.mark.lances
def test_deve_listar_lances_do_lote_sem_autenticacao(
    client, lote_ao_vivo, usuario_licitante, db_session
):
    lance = Lance(
        licitante_id=usuario_licitante.id,
        lote_id=lote_ao_vivo.id,
        valor=120,
    )
    db_session.add(lance)
    db_session.commit()

    response = client.get(f"/api/v1/lances/lotes/{lote_ao_vivo.id}")

    assert response.status_code == 200
    assert response.json()[0]["id"] == lance.id
    assert response.json()[0]["valor"] == "120.00"
    assert response.json()[0]["participante"] == "Participante #1"
    assert "licitante_id" not in response.json()[0]


@pytest.mark.lances
def test_deve_criar_lance_e_comprometer_saldo_quando_dados_validos(
    client,
    cabecalho_licitante,
    lote_ao_vivo,
    carteira_licitante,
    usuario_licitante,
    db_session,
):
    data_fim_original = lote_ao_vivo.data_fim
    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 110},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 201
    assert response.json()["lote_id"] == lote_ao_vivo.id
    assert response.json()["participante"] == "Participante #1"
    assert "licitante_id" not in response.json()
    assert response.json()["valor"] == "110.00"

    db_session.refresh(lote_ao_vivo)
    assert lote_ao_vivo.valor_atual == Decimal("110.00")
    assert lote_ao_vivo.data_fim == data_fim_original
    assert lote_ao_vivo.vencedor_id is None
    db_session.refresh(carteira_licitante)
    assert carteira_licitante.saldo_comprometido == Decimal("110.00")
    assert db_session.query(Lance).count() == 1


@pytest.mark.lances
def test_deve_estender_leilao_quando_lance_ocorrer_nos_dois_minutos_finais(
    client, cabecalho_licitante, lote_ao_vivo, carteira_licitante, db_session
):
    data_fim_original = utc_now_naive() + timedelta(seconds=90)
    lote_ao_vivo.data_fim = data_fim_original
    db_session.commit()

    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 110},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 201
    db_session.refresh(lote_ao_vivo)
    assert lote_ao_vivo.data_fim == data_fim_original + timedelta(minutes=2)


@pytest.mark.lances
def test_deve_liberar_saldo_do_lance_superado_e_comprometer_o_novo(
    client,
    cabecalho_outro_licitante,
    lote_ao_vivo,
    carteira_licitante,
    carteira_outro_licitante,
    usuario_licitante,
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

    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 131},
        headers=cabecalho_outro_licitante,
    )

    assert response.status_code == 201
    db_session.refresh(carteira_licitante)
    db_session.refresh(carteira_outro_licitante)
    db_session.refresh(lote_ao_vivo)
    assert carteira_licitante.saldo_comprometido == Decimal("0.00")
    assert carteira_outro_licitante.saldo_comprometido == Decimal("131.00")
    assert lote_ao_vivo.valor_atual == Decimal("131.00")
    assert lote_ao_vivo.vencedor_id is None


@pytest.mark.lances
def test_deve_rejeitar_lance_quando_lote_nao_estiver_disponivel(
    client, cabecalho_licitante, carteira_licitante
):
    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": 99999, "valor": 120},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Lote não encontrado."


@pytest.mark.lances
def test_deve_rejeitar_lance_quando_lote_ainda_nao_comecou(
    client, cabecalho_licitante, lote_teste, carteira_licitante
):
    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_teste.id, "valor": 120},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Este leilão ainda não começou."


@pytest.mark.lances
def test_deve_rejeitar_lance_quando_data_de_inicio_ainda_nao_chegou(
    client, cabecalho_licitante, lote_ao_vivo, carteira_licitante, db_session
):
    lote_ao_vivo.data_inicio = utc_now_naive() + timedelta(minutes=1)
    db_session.commit()

    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 120},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Este leilão ainda não começou."


@pytest.mark.lances
def test_deve_rejeitar_lance_quando_leilao_ja_foi_encerrado(
    client, cabecalho_licitante, lote_ao_vivo, carteira_licitante, db_session
):
    lote_ao_vivo.status = StatusLote.CONCLUIDO
    db_session.commit()

    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 120},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Este leilão já foi encerrado e não aceita novos lances."
    )


@pytest.mark.lances
def test_deve_rejeitar_lance_abaixo_do_incremento_minimo(
    client, cabecalho_licitante, lote_ao_vivo, carteira_licitante
):
    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 109},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Lance abaixo do mínimo. O próximo lance deve ser de pelo menos R$ 110,00."
    )


@pytest.mark.lances
def test_deve_rejeitar_lance_quando_saldo_disponivel_for_insuficiente(
    client, cabecalho_licitante, lote_ao_vivo, carteira_licitante
):
    carteira_licitante.saldo_total = Decimal("100.00")

    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 120},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Saldo insuficiente para este lance. Deposite ou informe um valor menor."
    )


@pytest.mark.lances
def test_deve_rejeitar_lance_se_usuario_tentar_cobrir_o_proprio_lance(
    client,
    cabecalho_licitante,
    lote_ao_vivo,
    carteira_licitante,
    usuario_licitante,
    db_session,
):
    db_session.add(
        Lance(
            licitante_id=usuario_licitante.id,
            lote_id=lote_ao_vivo.id,
            valor=120,
        )
    )
    db_session.commit()

    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 140},
        headers=cabecalho_licitante,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Você já está ganhando este lote; aguarde outro participante cobrir seu lance."
    )


@pytest.mark.lances
def test_deve_retornar_403_quando_leiloeiro_tentar_criar_lance(
    client, cabecalho_autenticado, lote_ao_vivo
):
    response = client.post(
        "/api/v1/lances/",
        json={"lote_id": lote_ao_vivo.id, "valor": 120},
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 403


@pytest.mark.lances
def test_deve_listar_lotes_com_lances_do_usuario_incluindo_perdidos(
    client,
    cabecalho_licitante,
    lote_teste,
    usuario_licitante,
    outro_usuario_licitante,
    db_session,
):
    lote_teste.status = StatusLote.CONCLUIDO
    lote_teste.vencedor_id = outro_usuario_licitante.id
    lote_teste.valor_atual = Decimal("180.00")
    db_session.add_all(
        [
            Lance(
                licitante_id=usuario_licitante.id,
                lote_id=lote_teste.id,
                valor=Decimal("120.00"),
            ),
            Lance(
                licitante_id=usuario_licitante.id,
                lote_id=lote_teste.id,
                valor=Decimal("150.00"),
            ),
            Lance(
                licitante_id=outro_usuario_licitante.id,
                lote_id=lote_teste.id,
                valor=Decimal("180.00"),
            ),
        ]
    )
    db_session.commit()

    response = client.get(
        "/api/v1/lances/meus?categoria=meus-lances",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["lote"]["id"] == lote_teste.id
    assert data["items"][0]["lote"]["item"]["titulo"] == "Nenúfares"
    assert data["items"][0]["lance"]["valor"] == "150.00"
    assert data["items"][0]["situacao"] == "superado"


@pytest.mark.lances
def test_deve_filtrar_lotes_arrematados_pelo_usuario_com_paginacao(
    client,
    cabecalho_licitante,
    lote_teste,
    usuario_licitante,
    db_session,
):
    lote_teste.status = StatusLote.CONCLUIDO
    lote_teste.vencedor_id = usuario_licitante.id
    db_session.add(
        Lance(
            licitante_id=usuario_licitante.id,
            lote_id=lote_teste.id,
            valor=Decimal("150.00"),
        )
    )
    db_session.commit()

    response = client.get(
        "/api/v1/lances/meus?categoria=lotes-vencidos&offset=0&limit=1",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["situacao"] == "arrematado"


@pytest.mark.lances
def test_deve_listar_historico_sem_expor_identidade_dos_outros_licitantes(
    client,
    cabecalho_licitante,
    lote_ao_vivo,
    usuario_licitante,
    outro_usuario_licitante,
    db_session,
):
    db_session.add_all(
        [
            Lance(
                licitante_id=usuario_licitante.id,
                lote_id=lote_ao_vivo.id,
                valor=Decimal("120.00"),
            ),
            Lance(
                licitante_id=outro_usuario_licitante.id,
                lote_id=lote_ao_vivo.id,
                valor=Decimal("140.00"),
            ),
        ]
    )
    db_session.commit()

    response = client.get(
        f"/api/v1/lances/lotes/{lote_ao_vivo.id}/historico?limit=1",
        headers=cabecalho_licitante,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["valor"] == "140.00"
    assert data["items"][0]["eh_usuario_atual"] is False
    assert "licitante_id" not in data["items"][0]


@pytest.mark.lances
def test_deve_rejeitar_consulta_dos_meus_lances_sem_autenticacao(client):
    response = client.get("/api/v1/lances/meus")

    assert response.status_code == 401


@pytest.mark.lances
def test_deve_rejeitar_historico_sem_autenticacao(client):
    response = client.get("/api/v1/lances/lotes/1/historico")

    assert response.status_code == 401