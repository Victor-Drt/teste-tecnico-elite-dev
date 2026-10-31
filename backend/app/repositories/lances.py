from sqlalchemy.orm import Session

from app.models.lances import Lance


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


def criar_lance(db: Session, usuario_id: int, lance: Lance):
    db.add(lance)
    db.commit()
    db.refresh(lance)
    return lance
