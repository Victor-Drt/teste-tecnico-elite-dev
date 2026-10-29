from sqlalchemy import Integer, String, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class Item(Base):
    __tablename__ = "itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_externo: Mapped[int] = mapped_column(Integer)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    numero_referencia: Mapped[str] = mapped_column(String, nullable=False)
    data_exibicao: Mapped[str] = mapped_column(String, nullable=False)
    info_artista: Mapped[str] = mapped_column(String, nullable=False)
    short_description: Mapped[str] = mapped_column(String, nullable=False)
    coletado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
