from sqlalchemy import Integer, String, func, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class Item(Base):
    __tablename__ = "itens"

    __table_args__ = (UniqueConstraint("id_externo", name="uq_itens_id_externo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_externo: Mapped[int] = mapped_column(Integer, nullable=False)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    numero_referencia: Mapped[str | None] = mapped_column(String, nullable=True)
    data_exibicao: Mapped[str | None] = mapped_column(String, nullable=True)
    info_artista: Mapped[str | None] = mapped_column(String, nullable=True)
    descricao: Mapped[str | None] = mapped_column(String, nullable=True)
    imagem_id: Mapped[str] = mapped_column(String, nullable=False)
    coletado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
