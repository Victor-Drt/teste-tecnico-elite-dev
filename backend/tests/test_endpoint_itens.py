import asyncio

import pytest

from app.models.itens import Item
from app.schemas.itens import ItensApiExterna
from app.services.itens import ItemService


@pytest.mark.itens
def test_deve_retornar_lista_de_itens_com_sucesso_quando_autenticado(
    client, cabecalho_autenticado, db_session
):
    itens = [
        {
            "id": 1,
            "titulo": "Item de teste",
            "data_exibicao": "2026",
            "info_artista": "Artista de teste",
            "imagem_id": "img-123",
        }
    ]
    db_session.add(
        Item(
            id_externo=123,
            titulo="Item de teste",
            numero_referencia="REF-123",
            data_exibicao="2026",
            info_artista="Artista de teste",
            descricao="Descrição do item",
            imagem_id="img-123",
        )
    )
    db_session.commit()

    response = client.get(
        "/api/v1/itens/",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 200
    assert response.json() == itens


@pytest.mark.itens
def test_deve_criar_ou_atualizar_item_sincronizado_sem_duplicar(
    db_session, monkeypatch
):
    respostas_api = [
        [
            ItensApiExterna(
                id=123,
                title="Item inicial",
                main_reference_number="REF-123",
                date_display="2026",
                artist_display="Artista de teste",
                short_description="Descrição inicial",
                image_id="img-123",
            )
        ],
        [
            ItensApiExterna(
                id=123,
                title="Item atualizado",
                main_reference_number="REF-123",
                date_display="2026",
                artist_display="Artista de teste",
                short_description="Descrição atualizada",
                image_id="img-456",
            )
        ],
    ]

    async def listar_itens_api_externa(self, page: int = 1, limit: int = 10):
        return respostas_api.pop(0)

    monkeypatch.setattr(
        ItemService,
        "listar_itens_api_externa",
        listar_itens_api_externa,
    )
    service = ItemService(db_session)

    assert asyncio.run(service.sincronizar_itens_api_externa()) == 1
    assert asyncio.run(service.sincronizar_itens_api_externa()) == 1

    itens = db_session.query(Item).all()
    assert len(itens) == 1
    assert itens[0].titulo == "Item atualizado"
    assert itens[0].descricao == "Descrição atualizada"
    assert itens[0].imagem_id == "img-456"


@pytest.mark.itens
def test_deve_sincronizar_todas_as_paginas_da_api_externa(db_session, monkeypatch):
    paginas_solicitadas = []

    async def listar_itens_api_externa(self, page: int = 1, limit: int = 10):
        paginas_solicitadas.append(page)
        quantidade = 10 if page == 1 else 1
        return [
            ItensApiExterna(
                id=(page - 1) * 10 + indice,
                title=f"Item {page}-{indice}",
                main_reference_number=f"REF-{page}-{indice}",
                date_display="2026",
                artist_display="Artista de teste",
                short_description="Descrição do item",
                image_id=f"img-{page}-{indice}",
            )
            for indice in range(quantidade)
        ]

    monkeypatch.setattr(
        ItemService,
        "listar_itens_api_externa",
        listar_itens_api_externa,
    )

    quantidade = asyncio.run(
        ItemService(db_session).sincronizar_itens_api_externa()
    )

    assert paginas_solicitadas == [1, 2]
    assert quantidade == 11
    assert db_session.query(Item).count() == 11


@pytest.mark.itens
@pytest.mark.parametrize(
    ("page", "limit"),
    [(1, 101), (101, 10), (0, 10), (1, 0)],
)
def test_deve_rejeitar_paginacao_fora_dos_limites_da_api_externa(
    db_session, page, limit
):
    with pytest.raises(ValueError):
        asyncio.run(
            ItemService(db_session).listar_itens_api_externa(page, limit)
        )


@pytest.mark.itens
def test_deve_limitar_sincronizacao_a_mil_itens(db_session, monkeypatch):
    paginas_solicitadas = []

    async def listar_itens_api_externa(self, page: int, limit: int):
        paginas_solicitadas.append((page, limit))
        return [
            ItensApiExterna(
                id=(page - 1) * limit + indice + 1,
                title=f"Item {page}-{indice}",
                main_reference_number=f"REF-{page}-{indice}",
                date_display="2026",
                artist_display="Artista de teste",
                short_description="Descrição do item",
                image_id=f"img-{page}-{indice}",
            )
            for indice in range(limit)
        ]

    monkeypatch.setattr(
        ItemService,
        "listar_itens_api_externa",
        listar_itens_api_externa,
    )

    quantidade = asyncio.run(
        ItemService(db_session).sincronizar_itens_api_externa(limit=100)
    )

    assert quantidade == 1000
    assert len(paginas_solicitadas) == 10
    assert paginas_solicitadas[-1] == (10, 100)
    assert db_session.query(Item).count() == 1000


@pytest.mark.itens
def test_deve_retornar_falha_quando_nao_autenticado(client):
    response = client.get("/api/v1/itens/")

    assert response.status_code == 401
    assert "detail" in response.json()
