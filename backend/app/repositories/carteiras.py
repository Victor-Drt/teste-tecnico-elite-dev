from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.carteiras import Carteira


def buscar_carteiras_para_atualizacao(
    db: Session, usuario_ids: list[int]
) -> list[Carteira]:
    return (
        db.query(Carteira)
        .filter(Carteira.usuario_id.in_(usuario_ids))
        .order_by(Carteira.usuario_id)
        .with_for_update()
        .all()
    )


def salvar_carteira(db: Session, carteira: Carteira) -> Carteira:
    db.add(carteira)
    db.commit()
    db.refresh(carteira)
    return carteira


def buscar_carteira_por_usuario_id(db: Session, usuario_id: int) -> Carteira | None:
    return db.query(Carteira).filter(Carteira.usuario_id == usuario_id).one_or_none()
