from sqlalchemy.orm import Session

from app.repositories import (
    lances as repository,
    lotes as lote_repository,
    carteiras as carteira_repository,
)
from app.schemas.lances import (
    CategoriaMeusLances,
    HistoricoLancesPagina,
    LanceCreate,
    LanceHistoricoItem,
    LanceResumo,
    MeuLanceItem,
    MeuLancePagina,
    SituacaoMeuLance,
)
from app.schemas.usuarios import UsuarioResponse
from app.models.lances import Lance
from app.models.lotes import StatusLote


class LanceService:
    def __init__(self, db: Session):
        self.db = db

    def listar_lances_por_lote(self, lote_id: int) -> list[LanceResumo]:

        lances = repository.listar_lances_por_lote_id(self.db, lote_id)

        return [LanceResumo.model_validate(lance) for lance in lances]

    def buscar_lance_por_id(self, usuario_id: int, lance_id: int) -> LanceResumo | None:

        lance = repository.buscar_lance_por_id(self.db, usuario_id, lance_id)

        if lance is None:
            raise ValueError("Lance não encontrado")

        return LanceResumo.model_validate(lance)

    def listar_meus_lances(
        self,
        usuario_id: int,
        categoria: CategoriaMeusLances,
        offset: int,
        limit: int,
    ) -> MeuLancePagina:
        lances, total = repository.listar_ultimos_lances_por_usuario(
            self.db, usuario_id, categoria.value, offset, limit
        )
        items = []

        for lance in lances:
            lote = lance.lote
            if lote.status == StatusLote.CONCLUIDO:
                situacao = (
                    SituacaoMeuLance.ARREMATADO
                    if lote.vencedor_id == usuario_id
                    else SituacaoMeuLance.SUPERADO
                )
            elif lance.valor == lote.valor_atual:
                situacao = SituacaoMeuLance.LIDERANDO
            else:
                situacao = SituacaoMeuLance.SUPERADO

            items.append(
                MeuLanceItem(
                    lote=lote,
                    lance=lance,
                    situacao=situacao,
                )
            )

        return MeuLancePagina(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
        )

    def listar_historico_lances(
        self, lote_id: int, usuario_id: int, offset: int, limit: int
    ) -> HistoricoLancesPagina:
        lances, total = repository.listar_historico_lances_por_lote(
            self.db, lote_id, offset, limit
        )
        items = [
            LanceHistoricoItem(
                valor=lance.valor,
                data_criacao=lance.data_criacao,
                eh_usuario_atual=lance.licitante_id == usuario_id,
            )
            for lance in lances
        ]
        return HistoricoLancesPagina(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
        )

    def criar_lance(
        self, usuario: UsuarioResponse, lance_data: LanceCreate
    ) -> LanceResumo:

        lote = lote_repository.buscar_lote_aberto_por_id(self.db, lance_data.lote_id)

        if lote is None:
            raise ValueError("Lote não disponivel")

        if usuario.papel.value != "licitante":
            raise ValueError("Somente licitantes podem fazer um lance")

        if lance_data.valor <= lote.incremento_minimo + lote.valor_atual:
            raise ValueError(
                "Lance não pode ser menor do que o valor minimo de um novo lance"
            )

        maior_lance = max(lote.lances, key=lambda lance: lance.valor, default=None)

        if maior_lance is not None and usuario.id == maior_lance.licitante_id:
            raise ValueError("Voce não pode cobrir seu proprio Lance")

        carteira = carteira_repository.buscar_carteira_por_usuario_id(
            self.db, usuario.id
        )

        if carteira is None:
            raise ValueError("Carteira não encontrada")

        saldo_disponivel = carteira.saldo_total - carteira.saldo_comprometido

        if lance_data.valor > saldo_disponivel:
            raise ValueError("Saldo insuficiente para efetuar este lance")

        carteira_lance_anterior = None
        if maior_lance is not None:
            carteira_lance_anterior = carteira_repository.buscar_carteira_por_usuario_id(
                self.db, maior_lance.licitante_id
            )
            if carteira_lance_anterior is None:
                raise ValueError("Carteira do licitante anterior não encontrada")

        if carteira_lance_anterior is not None:
            carteira_lance_anterior.saldo_comprometido -= maior_lance.valor

        lote.valor_atual = lance_data.valor
        lance_obj = Lance(**lance_data.model_dump(), licitante_id=usuario.id)

        lance = repository.criar_lance(self.db, lance_obj)

        if lance is None:
            raise ValueError("Não foi possivel efetuar lance")

        carteira.saldo_comprometido += lance.valor

        self.db.commit()
        self.db.refresh(lance)

        return LanceResumo.model_validate(lance)
