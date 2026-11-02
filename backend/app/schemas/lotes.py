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


class ItemDetalhesVitrine(ItemResumo):
    descricao: str | None = None


class LoteVitrineResponse(LoteResumo):
    incremento_minimo: Decimal
    item: ItemDetalhesVitrine


class LanceAuditoriaPublica(BaseModel):
    participante: str
    valor: Decimal
    data_criacao: datetime


class AuditoriaPublicaResponse(BaseModel):
    lote_id: int
    item: ItemResumo
    data_inicio: datetime
    data_fim: datetime
    valor_arrematado: Decimal
    vencedor: str
    total_participantes: int
    total_lances: int
    lances: list[LanceAuditoriaPublica]
    hash_sha256: str


class ComprovanteArremateResponse(BaseModel):
    id: int
    lote_id: int
    lance_id: int
    item: ItemResumo
    valor: Decimal
    data_inicio: datetime
    data_fim: datetime
    data_liquidacao: datetime


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
