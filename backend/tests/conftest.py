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
    from app.models.carteiras import Carteira
    from app.models.itens import Item
    from app.models.lances import Lance
    from app.models.liquidacoes import LiquidacaoLote
    from app.models.lotes import Lote
    from app.models.usuarios import Usuario

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        bind=engine,
        tables=[
            Usuario.__table__,
            Item.__table__,
            Lote.__table__,
            Carteira.__table__,
            Lance.__table__,
            LiquidacaoLote.__table__,
        ],
    )
    session = Session(bind=engine)

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(
            bind=engine,
            tables=[
                Usuario.__table__,
                Item.__table__,
                Lote.__table__,
                Carteira.__table__,
                Lance.__table__,
                LiquidacaoLote.__table__,
            ],
        )
        engine.dispose()


@pytest.fixture
def itens_catalogo_teste(db_session: Session):
    from app.models.itens import Item

    itens = [
        Item(
            id_externo=123,
            titulo="Nenúfares",
            numero_referencia="REF-123",
            data_exibicao="1916",
            info_artista="Claude Monet",
            descricao="Pintura",
            imagem_id="img-123",
        ),
        Item(
            id_externo=456,
            titulo="A noite estrelada",
            numero_referencia="REF-456",
            data_exibicao="1889",
            info_artista="Vincent van Gogh",
            descricao="Pintura",
            imagem_id="img-456",
        ),
        Item(
            id_externo=789,
            titulo="Estudo de Monet",
            numero_referencia="REF-789",
            data_exibicao="2020",
            info_artista="Artista desconhecido",
            descricao="Pintura",
            imagem_id="img-789",
        ),
    ]
    db_session.add_all(itens)
    db_session.commit()
    return itens


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

    return {"Cookie": f"access_token={token}"}


@pytest.fixture
def usuario_licitante(db_session: Session):
    from app.models.usuarios import Usuario

    usuario = Usuario(
        nome="Licitante de Teste",
        email="licitante@leilao.com",
        senha="senha-hash-de-teste",
        papel="LICITANTE",
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def outro_usuario_licitante(db_session: Session):
    from app.models.usuarios import Usuario

    usuario = Usuario(
        nome="Outro Licitante",
        email="outro.licitante@leilao.com",
        senha="senha-hash-de-teste",
        papel="LICITANTE",
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def cabecalho_licitante(usuario_licitante) -> dict[str, str]:
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": usuario_licitante.email, "exp": tempo_expiracao}
    token = jwt.encode(
        payload,
        os.environ["SECRET_KEY"],
        algorithm=os.environ["ALGORITHM"],
    )
    return {"Cookie": f"access_token={token}"}


@pytest.fixture
def cabecalho_outro_licitante(outro_usuario_licitante) -> dict[str, str]:
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": outro_usuario_licitante.email, "exp": tempo_expiracao}
    token = jwt.encode(
        payload,
        os.environ["SECRET_KEY"],
        algorithm=os.environ["ALGORITHM"],
    )
    return {"Cookie": f"access_token={token}"}


@pytest.fixture
def lote_teste(db_session: Session, itens_catalogo_teste, usuario_teste):
    from datetime import datetime

    from app.models.lotes import Lote

    lote = Lote(
        item_id=itens_catalogo_teste[0].id,
        leiloeiro_id=usuario_teste.id,
        valor_inicial=100,
        valor_atual=100,
        incremento_minimo=10,
        data_inicio=datetime(2030, 1, 1, 10),
        data_fim=datetime(2030, 1, 1, 12),
    )
    db_session.add(lote)
    db_session.commit()
    db_session.refresh(lote)
    return lote


@pytest.fixture
def lote_ao_vivo(db_session: Session, itens_catalogo_teste, usuario_teste):
    from datetime import datetime, timedelta

    from app.models.lotes import Lote, StatusLote

    lote = Lote(
        item_id=itens_catalogo_teste[0].id,
        leiloeiro_id=usuario_teste.id,
        valor_inicial=100,
        valor_atual=100,
        incremento_minimo=10,
        status=StatusLote.AO_VIVO,
        data_inicio=datetime.now() - timedelta(hours=1),
        data_fim=datetime.now() + timedelta(hours=1),
    )
    db_session.add(lote)
    db_session.commit()
    db_session.refresh(lote)
    return lote


@pytest.fixture
def carteira_licitante(db_session: Session, usuario_licitante):
    from decimal import Decimal

    from app.models.carteiras import Carteira

    carteira = Carteira(
        usuario_id=usuario_licitante.id,
        saldo_total=Decimal("1000.00"),
        saldo_comprometido=Decimal("0.00"),
    )
    db_session.add(carteira)
    db_session.commit()
    db_session.refresh(carteira)
    return carteira


@pytest.fixture
def carteira_outro_licitante(db_session: Session, outro_usuario_licitante):
    from decimal import Decimal

    from app.models.carteiras import Carteira

    carteira = Carteira(
        usuario_id=outro_usuario_licitante.id,
        saldo_total=Decimal("1000.00"),
        saldo_comprometido=Decimal("0.00"),
    )
    db_session.add(carteira)
    db_session.commit()
    db_session.refresh(carteira)
    return carteira
