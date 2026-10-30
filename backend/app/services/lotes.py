from sqlalchemy.orm import Session

from app.models.lotes import Lote
from app.schemas.lotes import LoteCreate, LoteDetalhesResponse, LoteResumo, LoteUpdate
from app.repositories import lotes as repository


class LoteService:
    def __init__(self, db: Session):
        self.db = db

    def criar_lote(self, leiloeiro_id: int, data: LoteCreate):

        lote = Lote(**data.model_dump(), leiloeiro_id=leiloeiro_id)

        return repository.criar_lote(self.db, lote)

    def buscar_lote_por_id(
        self, leiloeiro_id: int, lote_id: int
    ) -> LoteDetalhesResponse:
        lote = repository.buscar_lote_por_id(self.db, leiloeiro_id, lote_id)

        if lote is None:
            raise ValueError("Lote não encontrado")

        return LoteDetalhesResponse.model_validate(lote)

    def listar_lotes(
        self, leiloeiro_id: int, offset: int, limit: int
    ) -> list[LoteResumo]:

        lotes = repository.listar_lotes(self.db, leiloeiro_id, offset, limit)

        return [LoteResumo.model_validate(lote) for lote in lotes]

    def atualizar_lote(
        self, leiloeiro_id: int, lote_id: int, data: LoteUpdate
    ) -> LoteResumo:

        dados = data.model_dump(exclude_unset=True)

        lote_atualizado = repository.atualizar_lote(
            db=self.db, leiloeiro_id=leiloeiro_id, lote_id=lote_id, lote=dados
        )

        if lote_atualizado is None:
            raise ValueError("Lote não encontrado")

        return LoteResumo.model_validate(lote_atualizado)

    def deletar_lote(self, leiloeiro_id: int, lote_id: int) -> None:
        lote_deletado = repository.deletar_lote(self.db, leiloeiro_id, lote_id)

        if lote_deletado is None:
            raise ValueError("Lote não encontrado")

        return lote_deletado
