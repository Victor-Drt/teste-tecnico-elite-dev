from sqlalchemy import Integer, ForeignKey, Numeric, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from enum import Enum

from datetime import datetime

from app.db.base import Base


class StatusLote(Enum):
    EM_BREVE = "em_breve"
    AO_VIVO = "ao_vivo"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class Lote(Base):
    __tablename__ = "lotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("itens.id"), nullable=False)
    leiloeiro_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    valor_minimo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    incremento_minimo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    vencedor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )
    status: Mapped[StatusLote] = mapped_column(
        SQLEnum(StatusLote), nullable=False, default=StatusLote.EM_BREVE
    )

    data_inicio: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    data_fim: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    data_atualizacao: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=func.now()
    )

    item: Mapped["Item"] = relationship(back_populates="lotes")
    leiloeiro: Mapped["Usuario"] = relationship(
        back_populates="lotes_como_leiloeiro",
        foreign_keys=[leiloeiro_id],
    )
    vencedor: Mapped["Usuario | None"] = relationship(
        back_populates="lotes_como_vencedor",
        foreign_keys=[vencedor_id],
    )
    lances: Mapped[list["Lance"]] = relationship(back_populates="lote")
