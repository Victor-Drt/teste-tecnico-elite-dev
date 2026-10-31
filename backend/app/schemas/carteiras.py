from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

class CarteiraDeposito(BaseModel):
    valor: Decimal

class CarteiraResponse(BaseModel):
    id: int
    usuario_id: int
    saldo_total: Decimal
    saldo_comprometido: Decimal
    saldo_disponivel: Decimal
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
