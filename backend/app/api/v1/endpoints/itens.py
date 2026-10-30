from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.usuarios import UsuarioResponse
from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.services.itens import ItemService

router = APIRouter()


@router.get("/")
def listar_itens(
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
):
    service = ItemService(db)
    itens = service.listar_itens(offset, limit)

    return itens
