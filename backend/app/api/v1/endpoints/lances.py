from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.api.v1.deps import get_current_user, verificar_role
from app.db.session import get_db
from app.schemas.usuarios import UsuarioResponse
from app.schemas.lances import LanceResumo, LanceCreate
from app.services.lances import LanceService 

router = APIRouter()


@router.get("/lotes/{lote_id}", status_code=200)
def listar_lances(
    lote_id: int,
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[LanceResumo]:
    service = LanceService(db)

    return service.listar_lances_por_lote(lote_id)


@router.get("/{lance_id}", status_code=200)
def buscar_lance(
    lance_id: int,
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> LanceResumo:
    service = LanceService(db)

    try:
        return service.buscar_lance_por_id(usuario_atual.id, lance_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/", status_code=201)
def criar_lance(
    data: LanceCreate,
    usuario_atual: Annotated[UsuarioResponse, Depends(verificar_role("licitante"))],
    db: Session = Depends(get_db),
) -> LanceResumo:
    service = LanceService(db)

    return service.criar_lance(usuario_atual.id, data)
