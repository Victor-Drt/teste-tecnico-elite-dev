from sqlalchemy import Integer, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from decimal import Decimal

from app.db.base import Base


class Carteira(Base):
    __tablename__ = "carteiras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False, unique=True
    )
    saldo_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    saldo_comprometido: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="carteira")
