import pytest


@pytest.mark.usuarios
def test_deve_criar_usuario_com_sucesso_quando_dados_forem_validos(client):

    payload = {
        "nome": "UserTest",
        "email": "user@example.com",
        "senha": "testSenha",
        "papel": "leiloeiro",
    }

    response = client.post("/api/v1/usuarios/criar", json=payload)

    assert response.status_code == 201
    assert response.json()["nome"] == "UserTest"


@pytest.mark.usuarios
def test_deve_retornar_422_ao_criar_usuario_quando_dados_forem_invalidos(
    client,
):
    payload = {
        "nome": 1,
        "email": "email_invalido_sem_arroba",
        "senha": "testSenha",
        "papel": "leiloeiro",
    }

    response = client.post("/api/v1/usuarios/criar", json=payload)

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.usuarios
def test_deve_retornar_detalhes_do_usuario_quando_usuario_estiver_autenticado(
    client, cabecalho_autenticado
):
    response = client.get("/api/v1/usuarios/perfil", headers=cabecalho_autenticado)

    assert response.status_code == 200
    assert response.json()["email"] == "test@leilao.com"


@pytest.mark.usuarios
def test_deve_retornar_401_do_usuario_quando_token_nao_estiver_valido(
    client, cabecalho_autenticado
):
    response = client.get(
        "/api/v1/usuarios/perfil", headers={"Authorization": "Bearer token-errado"}
    )

    assert response.status_code == 401
    assert "detail" in response.json()
