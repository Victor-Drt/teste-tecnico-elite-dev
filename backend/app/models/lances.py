from sqlalchemy import Integer, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from decimal import Decimal

from app.db.base import Base


class Lance(Base):
    __tablename__ = "lances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    licitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    lote_id: Mapped[int] = mapped_column(ForeignKey("lotes.id"), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    licitante: Mapped["Usuario"] = relationship(
        back_populates="lances",
    )
    lote: Mapped["Lote"] = relationship(
        back_populates="lances",
    )
