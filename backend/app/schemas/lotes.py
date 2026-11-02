from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

from app.models.lotes import StatusLote
from app.schemas.itens import ItemResumo


class LoteCreate(BaseModel):
    item_id: int
    data_inicio: datetime
    data_fim: datetime
    valor_inicial: Decimal
    incremento_minimo: Decimal


class LoteResumo(BaseModel):
    id: int
    item_id: int
    data_inicio: datetime
    data_fim: datetime
    valor_atual: Decimal
    status: StatusLote
    vencedor_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class LoteListagemResponse(LoteResumo):
    item: ItemResumo


class LoteDetalhesResponse(LoteResumo):
    valor_inicial: Decimal
    incremento_minimo: Decimal
    leiloeiro_id: int
    data_criacao: datetime
    data_atualizacao: datetime | None = None


class LoteUpdate(BaseModel):
    item_id: int | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    valor_inicial: Decimal | None = None
    incremento_minimo: Decimal | None = None
    status: StatusLote | None = None
