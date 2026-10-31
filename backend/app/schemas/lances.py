from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


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
