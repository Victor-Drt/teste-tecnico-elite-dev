from sqlalchemy.orm import Session

from app.models.lotes import Lote
from app.schemas.lotes import LoteCreate
from app.repositories.lotes import criar_lote


class LoteService:
    def __init__(self, db: Session):
        self.db = db

    def criar_lote(self, leiloeiro_id: int, data: LoteCreate):

        lote = Lote(**data.model_dump(), leiloeiro_id=leiloeiro_id)

        return criar_lote(self.db, lote)
