import pytest


@pytest.mark.auth
def test_deve_retornar_access_token_quando_credenciais_forem_validas(client, usuario_teste):
    payload = {"email": "test@leilao.com", "senha": "senha123"}

    response = client.post("/api/v1/auth/token", json=payload)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.auth
def test_deve_retornar_401_quando_senha_for_incorreta(client, usuario_teste):
    payload = {"email": "test@emailerrado.com", "senha": "senha-errada"}

    response = client.post("/api/v1/auth/token", json=payload)

    assert response.status_code == 401
    assert "detail" in response.json()
