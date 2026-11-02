from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LiquidacaoLote(Base):
    __tablename__ = "liquidacoes_lotes"
    __table_args__ = (
        UniqueConstraint("lote_id", name="uq_liquidacoes_lotes_lote_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey("lotes.id"), nullable=False)
    leiloeiro_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False
    )
    vencedor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )
    lance_id: Mapped[int | None] = mapped_column(
        ForeignKey("lances.id"), nullable=True
    )
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_liquidacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    lote: Mapped["Lote"] = relationship()
    leiloeiro: Mapped["Usuario"] = relationship(foreign_keys=[leiloeiro_id])
    vencedor: Mapped["Usuario | None"] = relationship(foreign_keys=[vencedor_id])
    lance: Mapped["Lance | None"] = relationship()
