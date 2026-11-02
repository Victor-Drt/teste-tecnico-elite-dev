from decimal import Decimal

from sqlalchemy.orm import Session

from app.schemas.usuarios import UsuarioResponse, UsuarioCreate
from app.models.usuarios import Usuario
from app.models.carteiras import Carteira
from app.repositories import usuarios as repository
from app.core.security import hash_password


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db

    def criar_usuario(self, data: UsuarioCreate) -> UsuarioResponse:

        usuario = Usuario(
            nome=data.nome,
            email=data.email,
            senha=hash_password(data.senha),
            papel=data.papel,
            carteira=Carteira(
                saldo_total=Decimal("0.00"),
                saldo_comprometido=Decimal("0.00"),
            ),
        )

        novo_usuario = repository.criar_usuario(self.db, usuario)

        if novo_usuario is None:
            raise ValueError("E-mail já cadastrado")

        return UsuarioResponse.model_validate(novo_usuario)
