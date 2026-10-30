from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.session import get_db
from app.schemas.usuarios import UsuarioCreate, UsuarioResponse
from app.services.usuarios import UsuarioService
from app.api.v1.deps import get_current_user

router = APIRouter()


@router.post("/criar", status_code=201)
def criar_usuario(
    data: UsuarioCreate, db: Session = Depends(get_db)
) -> UsuarioResponse:
    service = UsuarioService(db)

    try:
        return service.criar_usuario(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get("/perfil", status_code=200)
def perfil(
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
) -> UsuarioResponse:
    return usuario_atual
