from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.usuarios import UsuarioResponse
from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.services.itens import ItemService
from app.schemas.itens import ItemResumo, ItemDetalhesResponse

router = APIRouter()


@router.get("/", status_code=200)
def listar_itens(
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
    query: str | None = None
) -> list[ItemResumo]:
    service = ItemService(db)
    itens = service.listar_itens(offset, limit, query)

    return itens


@router.get("/{item_id}", status_code=200)
def buscar_item(
    item_id: int,
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ItemDetalhesResponse:
    service = ItemService(db)

    try:
        return service.buscar_item_por_id(item_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
