from sqlalchemy.orm import Session
from decimal import Decimal

from app.repositories import carteiras as repository
from app.schemas.carteiras import CarteiraResponse, CarteiraDeposito
from app.models.carteiras import Carteira


class CarteiraService:
    def __init__(self, db: Session):
        self.db = db

    def depositar_valor(
        self, usuario_id: int, deposito: CarteiraDeposito
    ) -> CarteiraResponse:
        carteira = repository.buscar_carteira_por_usuario_id(self.db, usuario_id)

        if carteira is None:
            raise ValueError("Carteira não encontrada")

        carteira.saldo_total += deposito.valor

        carteira_atualizada = repository.salvar_carteira(self.db, carteira)

        return CarteiraResponse(
            id=carteira_atualizada.id,
            usuario_id=carteira_atualizada.usuario_id,
            saldo_total=carteira_atualizada.saldo_total,
            saldo_comprometido=carteira_atualizada.saldo_comprometido,
            saldo_disponivel=(
                carteira_atualizada.saldo_total - carteira_atualizada.saldo_comprometido
            ),
            data_criacao=carteira_atualizada.data_criacao,
        )

    def buscar_ou_criar_carteira(self, usuario_id: int) -> CarteiraResponse:
        carteira = repository.buscar_carteira_por_usuario_id(self.db, usuario_id)

        if carteira is None:

            carteira = Carteira(
                usuario_id=usuario_id,
                saldo_total=Decimal("0.00"),
                saldo_comprometido=Decimal("0.00"),
            )

            carteira = repository.salvar_carteira(self.db, carteira)

        return CarteiraResponse(
            id=carteira.id,
            usuario_id=carteira.usuario_id,
            saldo_total=carteira.saldo_total,
            saldo_comprometido=carteira.saldo_comprometido,
            saldo_disponivel=(carteira.saldo_total - carteira.saldo_comprometido),
            data_criacao=carteira.data_criacao,
        )
