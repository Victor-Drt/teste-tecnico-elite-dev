from sqlalchemy.orm import Session

from app.models.lotes import Lote


def criar_lote(db: Session, lote: Lote):
    db.add(lote)
    db.commit()
    db.refresh(lote)
    return lote


def buscar_lote_por_id(db: Session, leiloeiro_id: int, lote_id: int) -> Lote | None:
    return (
        db.query(Lote)
        .filter(Lote.id == lote_id, Lote.leiloeiro_id == leiloeiro_id)
        .one_or_none()
    )


def listar_lotes(db: Session, leiloeiro_id: int, offset: int, limit: int) -> list[Lote]:
    return (
        db.query(Lote)
        .filter(Lote.leiloeiro_id == leiloeiro_id)
        .order_by(Lote.data_criacao.desc(), Lote.data_inicio.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
