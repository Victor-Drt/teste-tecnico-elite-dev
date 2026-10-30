from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.usuarios import UsuarioResponse
from app.schemas.lotes import LoteCreate, LoteDetalhesResponse, LoteUpdate
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


@router.get("/", status_code=200)
def listar_lotes(
    usuario_atual: Annotated[
        UsuarioResponse,
        Depends(
            verificar_role(
                "leiloeiro",
            )
        ),
    ],
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
):
    service = LoteService(db)

    return service.listar_lotes(usuario_atual.id, offset, limit)


@router.get("/{lote_id}", status_code=200)
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


@router.patch("/{lote_id}", status_code=200)
def atualizar_lote(
    lote_id: int,
    data: LoteUpdate,
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
        return service.atualizar_lote(usuario_atual.id, lote_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete("/{lote_id}", status_code=204)
def deletar_lote(
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
        return service.deletar_lote(usuario_atual.id, lote_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
