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


@router.get("/{lote_id}")
def listar_lote_por_id(
    lote_id: int,
    usuario_atual: Annotated[
        UsuarioResponse,
        Depends(
            verificar_role(
                "leiloeiro",
            )
        ),
    ],
    db: Session = Depends(get_db),
):
    service = LoteService(db)

    try:
        return service.buscar_lote_por_id(usuario_atual.id, lote_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
