from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.api.v1.deps import get_current_user, verificar_role
from app.db.session import get_db
from app.schemas.usuarios import UsuarioResponse
from app.schemas.carteiras import CarteiraDeposito, CarteiraResponse
from app.services.carteiras import CarteiraService

router = APIRouter()


@router.post("/depositar", status_code=201)
def depositar_valor(
    deposito: CarteiraDeposito,
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> CarteiraResponse:
    service = CarteiraService(db)

    try:
        return service.depositar_valor(usuario_atual.id, deposito)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/minha")
def buscar_carteira(
    usuario_atual: Annotated[UsuarioResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> CarteiraResponse:
    service = CarteiraService(db)

    return service.buscar_ou_criar_carteira(usuario_atual.id)
