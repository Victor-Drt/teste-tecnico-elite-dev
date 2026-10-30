from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.usuarios import UsuarioResponse
from app.schemas.lotes import LoteCreate, LoteDetalhesResponse
from app.api.v1.deps import verificar_role
from app.db.session import get_db
from app.services.lotes import LoteService

router = APIRouter()


@router.post("/", status_code=201)
def criar_lote(
    data: LoteCreate,
    usuario_atual: Annotated[
        UsuarioResponse,
        Depends(
            verificar_role(
                "leiloeiro",
            )
        ),
    ],
    db: Session = Depends(get_db),
) -> LoteDetalhesResponse:
    service = LoteService(db)

    return service.criar_lote(usuario_atual.id, data)
