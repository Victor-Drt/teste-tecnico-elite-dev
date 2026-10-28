import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

os.environ.update(
    {
        "PROJECT_NAME": "Test API",
        "PROJECT_VERSION": "0.0.0",
        "SECRET_KEY": "test-secret-key-that-is-at-least-32-bytes-long",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "DATABASE_URL": "sqlite://",
    }
)


@pytest.fixture
def db_session() -> Iterator[Session]:
    from app.db.base import Base
    from app.models.usuarios import Usuario

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=[Usuario.__table__])
    session = Session(bind=engine)

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    from app.api.v1.deps import get_db
    from app.main import app

    previous_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


@pytest.fixture
def usuario_teste(db_session: Session):
    from app.models.usuarios import Usuario

    from app.core.security import hash_password

    usuario = Usuario(
        nome="Usuario de Teste",
        email="test@leilao.com",
        senha=hash_password("senha123"),
        papel="LEILOEIRO",
    )

    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    return usuario


from datetime import datetime, timedelta, timezone
import jwt


@pytest.fixture
def cabecalho_autenticado(usuario_teste) -> dict[str, str]:
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {"sub": usuario_teste.email, "exp": tempo_expiracao}

    token = jwt.encode(
        payload, os.environ["SECRET_KEY"], algorithm=os.environ["ALGORITHM"]
    )

    return {"Authorization": f"Bearer {token}"}
