from sqlalchemy.orm import Session

from app.models.lotes import Lote
from app.schemas.lotes import LoteCreate, LoteDetalhesResponse
from app.repositories import lotes as repository


class LoteService:
    def __init__(self, db: Session):
        self.db = db

    def criar_lote(self, leiloeiro_id: int, data: LoteCreate):

        lote = Lote(**data.model_dump(), leiloeiro_id=leiloeiro_id)

        return repository.criar_lote(self.db, lote)

    def buscar_lote_por_id(self, leiloeiro_id: int, lote_id: int) -> LoteDetalhesResponse:
        lote = repository.buscar_lote_por_id(self.db, leiloeiro_id, lote_id)

        if lote is None:
            raise ValueError("Lote não encontrado")

        return LoteDetalhesResponse.model_validate(lote)
