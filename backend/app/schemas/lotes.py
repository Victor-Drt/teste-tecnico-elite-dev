from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

from app.models.lotes import StatusLote


class LoteCreate(BaseModel):
    item_id: int
    data_inicio: datetime
    data_fim: datetime
    valor_minimo: Decimal
    incremento_minimo: Decimal

class LoteResumo(BaseModel):
    id: int
    item_id: int
    data_inicio: datetime
    data_fim: datetime
    status: StatusLote
    vencedor_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class LoteDetalhesResponse(LoteResumo):
    valor_minimo: Decimal
    incremento_minimo: Decimal
    leiloeiro_id: int
    data_criacao: datetime
    data_atualizacao: datetime | None = None
