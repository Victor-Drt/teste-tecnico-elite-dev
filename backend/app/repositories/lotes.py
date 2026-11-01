from sqlalchemy.orm import Session

from app.models.lotes import Lote, StatusLote


def criar_lote(db: Session, lote: Lote):
    db.add(lote)
    db.commit()
    db.refresh(lote)
    return lote


def buscar_lote_por_id(db: Session, lote_id: int) -> Lote | None:
    return (
        db.query(Lote)
        .filter(Lote.id == lote_id)
        .one_or_none()
    )


def buscar_lote_por_leiloeiro_id(
    db: Session, leiloeiro_id: int, lote_id: int
) -> Lote | None:
    return (
        db.query(Lote)
        .filter(Lote.id == lote_id, Lote.leiloeiro_id == leiloeiro_id)
        .one_or_none()
    )


def buscar_lote_aberto_por_id(db: Session, lote_id: int) -> Lote | None:
    return (
        db.query(Lote)
        .filter(Lote.id == lote_id, Lote.status == StatusLote.AO_VIVO)
        .one_or_none()
    )



def listar_lotes_por_leiloeiro(
    db: Session, leiloeiro_id: int, offset: int, limit: int
) -> list[Lote]:
    return (
        db.query(Lote)
        .filter(Lote.leiloeiro_id == leiloeiro_id)
        .order_by(Lote.data_criacao.desc(), Lote.data_inicio.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def listar_lotes(db: Session, offset: int, limit: int):
    return (
        db.query(Lote)
        .filter(Lote.status != StatusLote.CANCELADO)
        .order_by(Lote.data_criacao.desc(), Lote.data_inicio.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def listar_lotes_arrematados(db: Session, vencedor_id: int) -> list[Lote]:
    return (
        db.query(Lote)
        .filter(
            Lote.status == StatusLote.CONCLUIDO,
            Lote.vencedor_id == vencedor_id,
        )
        .order_by(Lote.data_fim.desc(), Lote.data_atualizacao.desc())
        .all()
    )


def atualizar_lote(
    db: Session, leiloeiro_id: int, lote_id: int, lote: dict
) -> Lote | None:
    lote_existente = (
        db.query(Lote)
        .filter(Lote.id == lote_id, Lote.leiloeiro_id == leiloeiro_id)
        .first()
    )

    if lote_existente is None:
        return None

    for key, value in lote.items():
        setattr(lote_existente, key, value)

    db.commit()
    db.refresh(lote_existente)
    return lote_existente


def deletar_lote(db: Session, leiloeiro_id: int, lote_id: int) -> None:
    lote_existente = buscar_lote_por_leiloeiro_id(db, leiloeiro_id, lote_id)

    if lote_existente is None:
        return None
    db.delete(lote_existente)
    db.commit()
    return lote_existente
