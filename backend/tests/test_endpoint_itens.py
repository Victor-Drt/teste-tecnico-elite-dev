import pytest

from app.services.itens import ItemService


@pytest.mark.itens
def test_deve_retornar_lista_de_itens_com_sucesso_quando_autenticado(
    client, cabecalho_autenticado, monkeypatch
):
    itens = [
        {
            "id_externo": 123,
            "titulo": "Item de teste",
            "numero_referencia": "REF-123",
            "data_exibicao": "2026",
            "info_artista": "Artista de teste",
            "short_description": "Descrição do item",
        }
    ]

    async def listar_itens(self, page: int = 1, limit: int = 10):
        return itens

    monkeypatch.setattr(ItemService, "listar_itens", listar_itens)

    response = client.get(
        "/api/v1/itens/",
        headers=cabecalho_autenticado,
    )

    assert response.status_code == 200
    assert response.json() == itens


@pytest.mark.itens
def test_deve_retornar_falha_quando_nao_autenticado(client):
    response = client.get("/api/v1/itens/")

    assert response.status_code == 401
    assert "detail" in response.json()
