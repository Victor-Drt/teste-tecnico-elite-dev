import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.time import utc_now_naive
from app.models.carteiras import Carteira
from app.models.lances import Lance
from app.models.liquidacoes import LiquidacaoLote
from app.models.lotes import Lote, StatusLote
from app.repositories import carteiras as carteira_repository
from app.repositories import lotes as repository
from app.repositories import usuarios as usuario_repository
from app.services.cadeia_lances import (
    HASH_INICIAL_CADEIA,
    mapear_participantes,
    obter_sufixo_cadeia,
    ordenar_lances,
    verificar_cadeia_lances,
)
from app.schemas.itens import ItemResumo
from app.schemas.lotes import (
    AuditoriaPublicaResponse,
    ComprovanteArremateResponse,
    LanceAuditoriaPublica,
    LoteCreate,
    LoteDetalhesResponse,
    LoteListagemResponse,
    LoteResumo,
    LoteUpdate,
    LoteVitrineResponse,
)
from app.schemas.usuarios import UsuarioResponse


class LoteRegraNegocioError(Exception):
    pass


class AuditoriaPublicaInconsistente(Exception):
    pass


class ComprovanteArremateInconsistente(Exception):
    pass


@dataclass(frozen=True)
class ResultadoEncerramento:
    lote_id: int
    vencedor_id: int | None
    valor_liquidado: Decimal


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

        lances = ordenar_lances(lote.lances)
        participante_por_id = mapear_participantes(lances)
        lances_publicos: list[LanceAuditoriaPublica] = []

        for lance in lances:
            participante = participante_por_id[lance.licitante_id]
            lances_publicos.append(
                LanceAuditoriaPublica(
                    participante=participante,
                    valor=lance.valor,
                    data_criacao=lance.data_criacao,
                    hash_anterior=lance.hash_anterior,
                    hash_evento=lance.hash_evento,
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
                    "hash_anterior": lance.hash_anterior,
                    "hash_evento": lance.hash_evento,
                }
                for lance in lances_publicos
            ],
        }
        liquidacao = repository.buscar_liquidacao_lote(self.db, lote_id)
        hash_ancora = (
            liquidacao.hash_cadeia_lances if liquidacao is not None else None
        )
        quantidade_ancorada = (
            liquidacao.quantidade_lances if liquidacao is not None else None
        )
        if hash_ancora is None or quantidade_ancorada is None:
            integridade_cadeia = "nao_verificada"
        elif quantidade_ancorada != len(lances):
            integridade_cadeia = "inconsistente"
        else:
            cadeia = obter_sufixo_cadeia(lances)
            if cadeia is None or not verificar_cadeia_lances(cadeia, hash_ancora):
                integridade_cadeia = "inconsistente"
            elif len(cadeia) != len(lances):
                integridade_cadeia = "nao_verificada"
            else:
                integridade_cadeia = "verificada"
        public_data["integridade_cadeia"] = integridade_cadeia
        public_data["hash_cadeia_lances"] = hash_ancora
        public_data["quantidade_lances_ancorada"] = quantidade_ancorada
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

    def buscar_comprovante_arremate(
        self, lote_id: int, vencedor_id: int
    ) -> ComprovanteArremateResponse:
        liquidacao = repository.buscar_comprovante_arremate(
            self.db, lote_id, vencedor_id
        )
        if liquidacao is None:
            raise ValueError("Comprovante de arremate não encontrado.")

        lance = liquidacao.lance
        lote = liquidacao.lote
        if (
            lance is None
            or liquidacao.lance_id is None
            or lance.lote_id != lote_id
            or lance.licitante_id != vencedor_id
            or lance.valor != liquidacao.valor
            or lote.status != StatusLote.CONCLUIDO
            or lote.vencedor_id != vencedor_id
        ):
            raise ComprovanteArremateInconsistente(
                f"O comprovante da liquidação {liquidacao.id} não corresponde "
                "ao lance vencedor registrado."
            )

        return ComprovanteArremateResponse(
            id=liquidacao.id,
            lote_id=liquidacao.lote_id,
            lance_id=liquidacao.lance_id,
            item=ItemResumo.model_validate(lote.item),
            valor=liquidacao.valor,
            data_inicio=lote.data_inicio,
            data_fim=lote.data_fim,
            data_liquidacao=liquidacao.data_liquidacao,
        )

    def buscar_lote_ao_vivo(self, lote_id: int) -> LoteDetalhesResponse:
        lote = repository.buscar_lote_aberto_por_id(self.db, lote_id)
        if lote is None:
            raise ValueError("Lote não encontrado ou não está ao vivo")

        return LoteDetalhesResponse.model_validate(lote)

    def encerrar_lote_expirado(
        self, lote_id: int, agora: datetime | None = None
    ) -> ResultadoEncerramento | None:
        agora = agora or utc_now_naive()

        try:
            lote = repository.buscar_lote_expirado_para_encerramento(
                self.db, lote_id, agora
            )
            if lote is None:
                return None

            lance_vencedor = max(
                lote.lances,
                key=lambda lance: (lance.valor, lance.id),
                default=None,
            )
            vencedor_id = (
                lance_vencedor.licitante_id if lance_vencedor is not None else None
            )
            valor_liquidado = (
                lance_vencedor.valor
                if lance_vencedor is not None
                else Decimal("0.00")
            )
            if lance_vencedor is None and lote.valor_atual != lote.valor_inicial:
                raise ValueError(
                    f"O lote {lote.id} não possui lances, mas seu valor atual "
                    "difere do valor inicial."
                )
            if lance_vencedor is not None and lance_vencedor.valor != lote.valor_atual:
                raise ValueError(
                    f"O maior lance do lote {lote.id} não corresponde ao valor atual."
                )

            if not repository.marcar_lote_concluido(
                self.db, lote.id, agora, vencedor_id
            ):
                self.db.rollback()
                return None

            if lance_vencedor is not None:
                if vencedor_id == lote.leiloeiro_id:
                    raise ValueError(
                        f"O leiloeiro não pode ser vencedor do próprio lote {lote.id}."
                    )

                leiloeiro = usuario_repository.buscar_usuario_para_atualizacao(
                    self.db, lote.leiloeiro_id
                )
                if leiloeiro is None:
                    raise ValueError(
                        f"Leiloeiro do lote {lote.id} não foi encontrado."
                    )

                carteiras = carteira_repository.buscar_carteiras_para_atualizacao(
                    self.db, sorted({lote.leiloeiro_id, vencedor_id})
                )
                carteiras_por_usuario = {
                    carteira.usuario_id: carteira for carteira in carteiras
                }
                carteira_vencedor = carteiras_por_usuario.get(vencedor_id)
                if carteira_vencedor is None:
                    raise ValueError(
                        f"Carteira do vencedor {vencedor_id} do lote {lote.id} "
                        "não foi encontrada; a liquidação foi cancelada para "
                        "evitar alterar saldos sem uma carteira válida."
                    )

                carteira_leiloeiro = carteiras_por_usuario.get(lote.leiloeiro_id)
                if carteira_leiloeiro is None:
                    carteira_leiloeiro = Carteira(
                        usuario_id=lote.leiloeiro_id,
                        saldo_total=Decimal("0.00"),
                        saldo_comprometido=Decimal("0.00"),
                    )
                    self.db.add(carteira_leiloeiro)
                    self.db.flush()

                if carteira_vencedor.saldo_total < valor_liquidado:
                    raise ValueError(
                        f"Saldo total insuficiente para liquidar o lote {lote.id}."
                    )
                if carteira_vencedor.saldo_comprometido < valor_liquidado:
                    raise ValueError(
                        f"Saldo comprometido insuficiente para liquidar o lote {lote.id}."
                    )

                carteira_vencedor.saldo_total -= valor_liquidado
                carteira_vencedor.saldo_comprometido -= valor_liquidado
                carteira_leiloeiro.saldo_total += valor_liquidado

            lances_ordenados = ordenar_lances(lote.lances)
            if not lances_ordenados:
                hash_cadeia_lances = HASH_INICIAL_CADEIA
            elif lances_ordenados[-1].hash_evento:
                hash_cadeia_lances = lances_ordenados[-1].hash_evento
            else:
                hash_cadeia_lances = None

            liquidacao = LiquidacaoLote(
                lote_id=lote.id,
                leiloeiro_id=lote.leiloeiro_id,
                vencedor_id=vencedor_id,
                lance_id=lance_vencedor.id if lance_vencedor is not None else None,
                valor=valor_liquidado,
                hash_cadeia_lances=hash_cadeia_lances,
                quantidade_lances=len(lances_ordenados),
                data_liquidacao=agora,
            )
            self.db.add(liquidacao)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return ResultadoEncerramento(
            lote_id=lote_id,
            vencedor_id=vencedor_id,
            valor_liquidado=valor_liquidado,
        )

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

        lote = repository.buscar_lote_por_leiloeiro_id(
            self.db, leiloeiro_id, lote_id
        )
        if lote is None:
            raise ValueError("Lote não encontrado")
        if lote.status == StatusLote.CONCLUIDO:
            raise LoteRegraNegocioError(
                "Um lote concluído não pode ser alterado"
            )

        if dados.get("status") == StatusLote.CONCLUIDO:
            raise LoteRegraNegocioError(
                "Lotes são concluídos automaticamente ao atingir o prazo final"
            )

        if dados.get("status") == StatusLote.CANCELADO:
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
