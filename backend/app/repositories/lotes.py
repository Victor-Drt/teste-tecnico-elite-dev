from sqlalchemy.orm import Session

from app.models.lotes import Lote


def criar_lote(db: Session, lote: Lote):
    db.add(lote)
    db.commit()
    db.refresh(lote)
    return lote
