from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.lances import Lance
from app.models.lotes import Lote, StatusLote


def listar_lances_por_lote_id(db: Session, lote_id: int) -> list[Lance]:
    return (
        db.query(Lance)
        .filter(Lance.lote_id == lote_id)
        .order_by(Lance.valor.desc())
        .all()
    )


def buscar_lance_por_id(db: Session, usuario_id: int, lance_id: int) -> Lance | None:
    return (
        db.query(Lance)
        .filter(Lance.id == lance_id, Lance.licitante_id == usuario_id)
        .one_or_none()
    )


def listar_ultimos_lances_por_usuario(
    db: Session,
    usuario_id: int,
    categoria: str,
    offset: int,
    limit: int,
) -> tuple[list[Lance], int]:
    ultimos_lances = (
        db.query(
            Lance.id.label("lance_id"),
            func.row_number()
            .over(
                partition_by=Lance.lote_id,
                order_by=(Lance.data_criacao.desc(), Lance.id.desc()),
            )
            .label("posicao"),
        )
        .filter(Lance.licitante_id == usuario_id)
        .subquery()
    )
    query = (
        db.query(Lance)
        .join(ultimos_lances, Lance.id == ultimos_lances.c.lance_id)
        .filter(ultimos_lances.c.posicao == 1)
        .join(Lote, Lance.lote_id == Lote.id)
        .options(joinedload(Lance.lote).joinedload(Lote.item))
    )

    if categoria == "lotes-vencidos":
        query = query.filter(
            Lote.status == StatusLote.CONCLUIDO,
            Lote.vencedor_id == usuario_id,
        )
    else:
        query = query.filter(
            (Lote.status != StatusLote.CONCLUIDO)
            | (Lote.vencedor_id != usuario_id)
            | (Lote.vencedor_id.is_(None))
        )

    total = query.count()
    lances = (
        query.order_by(Lance.data_criacao.desc(), Lance.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return lances, total


def listar_historico_lances_por_lote(
    db: Session, lote_id: int, offset: int, limit: int
) -> tuple[list[Lance], int]:
    query = db.query(Lance).filter(Lance.lote_id == lote_id)
    total = query.count()
    lances = (
        query.order_by(Lance.data_criacao.desc(), Lance.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return lances, total


def criar_lance(db: Session, lance: Lance):
    db.add(lance)
    db.flush()
    return lance
