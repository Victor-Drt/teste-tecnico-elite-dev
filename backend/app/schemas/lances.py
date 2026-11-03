from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from decimal import Decimal
from enum import Enum

from app.core.time import to_utc_datetime
from app.schemas.lotes import LoteListagemResponse


class LanceCreate(BaseModel):
    lote_id: int
    valor: Decimal


class LanceResumo(BaseModel):
    id: int
    licitante_id: int
    lote_id: int
    valor: Decimal
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("data_criacao", when_used="json")
    def serializar_data_em_utc(self, value: datetime) -> str:
        return to_utc_datetime(value).isoformat()


class LancePublico(BaseModel):
    id: int
    participante: str
    lote_id: int
    valor: Decimal
    data_criacao: datetime

    @field_serializer("data_criacao", when_used="json")
    def serializar_data_em_utc(self, value: datetime) -> str:
        return to_utc_datetime(value).isoformat()


class CategoriaMeusLances(str, Enum):
    MEUS_LANCES = "meus-lances"
    LOTES_VENCIDOS = "lotes-vencidos"


class SituacaoMeuLance(str, Enum):
    LIDERANDO = "liderando"
    SUPERADO = "superado"
    ARREMATADO = "arrematado"


class MeuLanceItem(BaseModel):
    lote: LoteListagemResponse
    lance: LanceResumo
    situacao: SituacaoMeuLance


class MeuLancePagina(BaseModel):
    items: list[MeuLanceItem]
    total: int
    offset: int
    limit: int


class LanceHistoricoItem(BaseModel):
    valor: Decimal
    data_criacao: datetime
    eh_usuario_atual: bool

    @field_serializer("data_criacao", when_used="json")
    def serializar_data_em_utc(self, value: datetime) -> str:
        return to_utc_datetime(value).isoformat()


class HistoricoLancesPagina(BaseModel):
    items: list[LanceHistoricoItem]
    total: int
    offset: int
    limit: int
