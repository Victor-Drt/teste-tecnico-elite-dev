import hashlib
import json

from sqlalchemy.orm import Session

from app.models.lotes import Lote, StatusLote
from app.schemas.usuarios import UsuarioResponse
from app.schemas.lotes import (
    AuditoriaPublicaResponse,
    LanceAuditoriaPublica,
    LoteCreate,
    LoteDetalhesResponse,
    LoteListagemResponse,
    LoteResumo,
    LoteUpdate,
    LoteVitrineResponse,
)
from app.schemas.itens import ItemResumo
from app.repositories import lotes as repository


class LoteRegraNegocioError(Exception):
    pass


class AuditoriaPublicaInconsistente(Exception):
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

    def buscar_lote_para_vitrine(self, lote_id: int) -> LoteVitrineResponse:
        lote = repository.buscar_lote_para_vitrine(self.db, lote_id)

        if lote is None:
            raise ValueError("Lote não encontrado")

        return LoteVitrineResponse.model_validate(lote)

    def buscar_auditoria_publica(self, lote_id: int) -> AuditoriaPublicaResponse:
        lote = repository.buscar_lote_para_auditoria(self.db, lote_id)
        if lote is None:
            raise ValueError("Auditoria pública não encontrada")

        lances = sorted(
            lote.lances,
            key=lambda lance: (lance.data_criacao, lance.id),
        )
        participante_por_id: dict[int, str] = {}
        lances_publicos: list[LanceAuditoriaPublica] = []

        for lance in lances:
            participante = participante_por_id.get(lance.licitante_id)
            if participante is None:
                participante = f"Participante #{len(participante_por_id) + 1}"
                participante_por_id[lance.licitante_id] = participante
            lances_publicos.append(
                LanceAuditoriaPublica(
                    participante=participante,
                    valor=lance.valor,
                    data_criacao=lance.data_criacao,
                )
            )

        if lote.vencedor_id is None:
            raise AuditoriaPublicaInconsistente(
                "O lote concluído não possui vencedor registrado."
            )

        vencedor = participante_por_id.get(lote.vencedor_id)
        if vencedor is None:
            raise AuditoriaPublicaInconsistente(
                "O lote concluído não possui lance registrado para o vencedor."
            )

        maior_valor = max(lance.valor for lance in lances)
        if (
            maior_valor != lote.valor_atual
            or not any(
                lance.licitante_id == lote.vencedor_id
                and lance.valor == maior_valor
                for lance in lances
            )
        ):
            raise AuditoriaPublicaInconsistente(
                "Os dados de encerramento não correspondem ao histórico de lances."
            )

        item = ItemResumo.model_validate(lote.item)
        public_data = {
            "lote_id": lote.id,
            "item": item.model_dump(mode="json"),
            "data_inicio": lote.data_inicio.isoformat(),
            "data_fim": lote.data_fim.isoformat(),
            "valor_arrematado": format(lote.valor_atual, ".2f"),
            "vencedor": vencedor,
            "total_participantes": len(participante_por_id),
            "total_lances": len(lances_publicos),
            "lances": [
                {
                    "participante": lance.participante,
                    "valor": format(lance.valor, ".2f"),
                    "data_criacao": lance.data_criacao.isoformat(),
                }
                for lance in lances_publicos
            ],
        }
        hash_sha256 = hashlib.sha256(
            json.dumps(
                public_data,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        return AuditoriaPublicaResponse(
            **public_data,
            hash_sha256=hash_sha256,
        )

    def buscar_lote_ao_vivo(self, lote_id: int) -> LoteDetalhesResponse:
        lote = repository.buscar_lote_aberto_por_id(self.db, lote_id)
        if lote is None:
            raise ValueError("Lote não encontrado ou não está ao vivo")

        return LoteDetalhesResponse.model_validate(lote)

    def listar_lotes(
        self,
        usuario: UsuarioResponse,
        offset: int,
        limit: int,
        status: StatusLote | None = None,
    ) -> list[LoteListagemResponse]:

        if usuario.papel.value == "leiloeiro":
            lotes = repository.listar_lotes_por_leiloeiro(
                self.db, usuario.id, offset, limit, status
            )
        else:
            lotes = repository.listar_lotes(self.db, offset, limit, status)

        return [LoteListagemResponse.model_validate(lote) for lote in lotes]

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
