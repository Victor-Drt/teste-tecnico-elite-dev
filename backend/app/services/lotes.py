from sqlalchemy.orm import Session

from app.models.lotes import Lote, StatusLote
from app.schemas.usuarios import UsuarioResponse
from app.schemas.lotes import LoteCreate, LoteDetalhesResponse, LoteResumo, LoteUpdate
from app.repositories import lotes as repository


class LoteRegraNegocioError(Exception):
    pass


class LoteService:
    def __init__(self, db: Session):
        self.db = db

    def criar_lote(self, leiloeiro_id: int, data: LoteCreate):
        lote = Lote(
            **data.model_dump(),
            leiloeiro_id=leiloeiro_id,
            valor_atual=data.valor_inicial,
        )

        return repository.criar_lote(self.db, lote)

    def buscar_lote_por_id(self, lote_id: int) -> LoteDetalhesResponse:
        lote = repository.buscar_lote_por_id(self.db, lote_id)

        if lote is None:
            raise ValueError("Lote não encontrado")

        return LoteDetalhesResponse.model_validate(lote)

    def buscar_lote_ao_vivo(self, lote_id: int) -> LoteDetalhesResponse:
        lote = repository.buscar_lote_aberto_por_id(self.db, lote_id)
        if lote is None:
            raise ValueError("Lote não encontrado ou não está ao vivo")

        return LoteDetalhesResponse.model_validate(lote)

    def listar_lotes(
        self, usuario: UsuarioResponse, offset: int, limit: int
    ) -> list[LoteResumo]:

        if usuario.papel.value == "leiloeiro":
            lotes = repository.listar_lotes_por_leiloeiro(
                self.db, usuario.id, offset, limit
            )
        else:
            lotes = repository.listar_lotes(self.db, offset, limit)

        return [LoteResumo.model_validate(lote) for lote in lotes]

    def atualizar_lote(
        self, leiloeiro_id: int, lote_id: int, data: LoteUpdate
    ) -> LoteResumo:
        dados = data.model_dump(exclude_unset=True)

        if dados.get("status") == StatusLote.CANCELADO:
            lote = repository.buscar_lote_por_leiloeiro_id(
                self.db, leiloeiro_id, lote_id
            )
            if lote is None:
                raise ValueError("Lote não encontrado")
            if lote.lances:
                raise LoteRegraNegocioError(
                    "Não é possível cancelar um lote que já recebeu lances"
                )

        lote_atualizado = repository.atualizar_lote(
            db=self.db, leiloeiro_id=leiloeiro_id, lote_id=lote_id, lote=dados
        )

        if lote_atualizado is None:
            raise ValueError("Lote não encontrado")

        return LoteResumo.model_validate(lote_atualizado)

    def deletar_lote(self, leiloeiro_id: int, lote_id: int) -> None:
        lote = repository.buscar_lote_por_leiloeiro_id(self.db, leiloeiro_id, lote_id)
        if lote is None:
            raise ValueError("Lote não encontrado")
        if lote.status.value == "ao_vivo":
            raise LoteRegraNegocioError(
                "Não é possível excluir um lote que está ao vivo"
            )
        if lote.lances:
            raise LoteRegraNegocioError(
                "Não é possível excluir um lote que já recebeu lances"
            )

        lote_deletado = repository.deletar_lote(self.db, leiloeiro_id, lote_id)

        if lote_deletado is None:
            raise ValueError("Lote não encontrado")

        return lote_deletado

    def buscar_lotes_arrematados(self, vencedor_id: int) -> list[LoteResumo]:
        lotes = repository.listar_lotes_arrematados(self.db, vencedor_id)
        return [LoteResumo.model_validate(lote) for lote in lotes]
