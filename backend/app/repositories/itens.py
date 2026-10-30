from typing import Sequence

from sqlalchemy import func, select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.itens import Item
from app.schemas.itens import ItensApiExterna


def listar_itens(db: Session, offset: int, limit: int, query: str | None) -> list[Item]:

    stmt = db.query(Item)

    if query:
        stmt = stmt.filter(
            or_(Item.titulo.ilike(f"%{query}%"), Item.info_artista.ilike(f"%{query}%"))
        )

    return stmt.offset(offset).limit(limit).all()

def buscar_item_por_id(db: Session, item_id: int) -> Item | None:
    return db.query(Item).filter(Item.id == item_id).one_or_none()


def salvar_ou_atualizar_itens(
    db: Session, itens_externos: Sequence[ItensApiExterna]
) -> int:
    itens_por_id = {item.id_externo: item for item in itens_externos}
    if not itens_por_id:
        return 0

    itens_existentes = db.scalars(
        select(Item).where(Item.id_externo.in_(itens_por_id))
    ).all()
    itens_por_id_externo = {item.id_externo: item for item in itens_existentes}

    for id_externo, item_externo in itens_por_id.items():
        valores = {
            "titulo": item_externo.titulo,
            "numero_referencia": item_externo.numero_referencia,
            "data_exibicao": item_externo.data_exibicao,
            "info_artista": item_externo.info_artista,
            "descricao": item_externo.short_description,
            "imagem_id": item_externo.image_id,
        }

        item_local = itens_por_id_externo.get(id_externo)
        if item_local is None:
            item_local = Item(id_externo=id_externo, **valores)
            db.add(item_local)
            itens_por_id_externo[id_externo] = item_local
        else:
            for campo, valor in valores.items():
                setattr(item_local, campo, valor)
            item_local.coletado_em = func.now()

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return len(itens_por_id)
