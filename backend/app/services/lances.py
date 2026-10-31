from sqlalchemy.orm import Session

from app.repositories import lances as repository
from app.schemas.lances import LanceResumo, LanceCreate
from app.models.lances import Lance


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

    def criar_lance(self, usuario_id: int, lance_data: LanceCreate) -> LanceResumo:

        # adicionar regras de negocio
        # 1. Verificar se o lote existe.
        # 2. Verificar se está aberto para lances.
        # 3. Verificar se o usuário pode dar lances.
        # 4. Verificar o valor mínimo permitido.
        # 5. Verificar o saldo disponível, conforme a regra definida para a carteira.
        # 6. Registrar o lance.
        # 7. Notificar os participantes pelo WebSocket após a confirmação da transação.

        lance_obj = Lance(**lance_data.model_dump(), licitante_id=usuario_id)

        lance = repository.criar_lance(self.db, lance_obj)

        return LanceResumo.model_validate(lance)
