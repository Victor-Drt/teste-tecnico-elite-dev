from sqlalchemy import String, Integer, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enum import Enum
from datetime import datetime

from app.db.base import Base


class PapelUsuario(Enum):
    LEILOEIRO = "leiloeiro"
    LICITANTE = "licitante"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    senha: Mapped[str] = mapped_column(String(100), nullable=False)
    papel: Mapped[PapelUsuario] = mapped_column(
        SQLEnum(PapelUsuario), nullable=False, default=PapelUsuario.LICITANTE
    )
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    lotes_como_leiloeiro: Mapped[list["Lote"]] = relationship(
        back_populates="leiloeiro",
        foreign_keys="Lote.leiloeiro_id",
    )
    lotes_como_vencedor: Mapped[list["Lote"]] = relationship(
        back_populates="vencedor",
        foreign_keys="Lote.vencedor_id",
    )
