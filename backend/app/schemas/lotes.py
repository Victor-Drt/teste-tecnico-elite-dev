from typing import Literal

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator

from app.models.lotes import StatusLote
from app.schemas.itens import ItemResumo
from app.core.time import to_utc_datetime, to_utc_naive


class LoteCreate(BaseModel):
    item_id: int
    data_inicio: datetime
    data_fim: datetime
    valor_inicial: Decimal
    incremento_minimo: Decimal

    @field_validator("data_inicio", "data_fim")
    @classmethod
    def normalizar_data_para_utc(cls, value: datetime) -> datetime:
        return to_utc_naive(value)


class LoteResumo(BaseModel):
    id: int
    item_id: int
    data_inicio: datetime
    data_fim: datetime
    valor_atual: Decimal
    status: StatusLote
    vencedor_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("data_inicio", "data_fim", when_used="json")
    def serializar_datas_em_utc(self, value: datetime) -> str:
        return to_utc_datetime(value).isoformat()


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
    hash_anterior: str | None
    hash_evento: str | None

    @field_serializer("data_criacao", when_used="json")
    def serializar_data_em_utc(self, value: datetime) -> str:
        return to_utc_datetime(value).isoformat()


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
    integridade_cadeia: Literal["verificada", "inconsistente", "nao_verificada"]
    hash_cadeia_lances: str | None
    quantidade_lances_ancorada: int | None

    @field_serializer("data_inicio", "data_fim", when_used="json")
    def serializar_datas_em_utc(self, value: datetime) -> str:
        return to_utc_datetime(value).isoformat()


class ComprovanteArremateResponse(BaseModel):
    id: int
    lote_id: int
    lance_id: int
    item: ItemResumo
    valor: Decimal
    data_inicio: datetime
    data_fim: datetime
    data_liquidacao: datetime

    @field_serializer(
        "data_inicio",
        "data_fim",
        "data_liquidacao",
        when_used="json",
    )
    def serializar_datas_em_utc(self, value: datetime) -> str:
        return to_utc_datetime(value).isoformat()


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

    @field_validator("data_inicio", "data_fim")
    @classmethod
    def normalizar_data_para_utc(
        cls, value: datetime | None
    ) -> datetime | None:
        return to_utc_naive(value) if value is not None else None
