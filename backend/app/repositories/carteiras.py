from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.carteiras import Carteira


def salvar_carteira(db: Session, carteira: Carteira) -> Carteira:
    db.add(carteira)
    db.commit()
    db.refresh(carteira)
    return carteira


def buscar_carteira_por_usuario_id(db: Session, usuario_id: int) -> Carteira | None:
    return db.query(Carteira).filter(Carteira.usuario_id == usuario_id).one_or_none()
