from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.usuarios import UsuarioCreate, UsuarioResponse
from app.services.usuarios import UsuarioService

router = APIRouter()


@router.post("/criar")
def criar_usuario(
    data: UsuarioCreate, db: Session = Depends(get_db)
) -> UsuarioResponse:
    service = UsuarioService(db)

    try:
        return service.criar_usuario(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )
