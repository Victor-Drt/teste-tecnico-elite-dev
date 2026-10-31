import pytest


@pytest.mark.auth
def test_deve_retornar_access_token_quando_credenciais_forem_validas(client, usuario_teste):
    payload = {"email": "test@leilao.com", "senha": "senha123"}

    response = client.post("/api/v1/auth/token", json=payload)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    set_cookie = response.headers["set-cookie"]
    assert "access_token=" in set_cookie
    assert "httponly" in set_cookie.lower()
    assert "secure" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()


@pytest.mark.auth
def test_cookie_emitido_no_login_autentica_requisicoes_protegidas(
    client, usuario_teste
):
    login_response = client.post(
        "/api/v1/auth/token",
        json={"email": "test@leilao.com", "senha": "senha123"},
    )
    access_token = login_response.cookies["access_token"]

    response = client.get(
        "/api/v1/usuarios/perfil",
        headers={"Cookie": f"access_token={access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == usuario_teste.email


@pytest.mark.auth
def test_deve_retornar_401_quando_senha_for_incorreta(client, usuario_teste):
    payload = {"email": "test@leilao.com", "senha": "senha-errada"}

    response = client.post("/api/v1/auth/token", json=payload)

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.auth
def test_deve_remover_cookie_ao_fazer_logout(client):
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert "access_token=" in response.headers["set-cookie"]
    assert "max-age=0" in response.headers["set-cookie"].lower()
