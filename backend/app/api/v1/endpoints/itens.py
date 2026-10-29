from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.usuarios import UsuarioResponse
from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.services.itens import ItemService

router = APIRouter()


@router.get("/")
async def listar_itens(
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
):
    service = ItemService(db)

    itens = await service.listar_itens(page, limit)

    return itens
