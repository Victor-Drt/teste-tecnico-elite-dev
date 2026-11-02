from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.usuarios import UsuarioResponse
from app.models.lotes import StatusLote
from app.schemas.lotes import (
    LoteCreate,
    LoteDetalhesResponse,
    LoteListagemResponse,
    LoteUpdate,
)
from app.api.v1.deps import verificar_role, get_current_user
from app.db.session import get_db
from app.services.lotes import LoteRegraNegocioError, LoteService

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
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    status_lote: StatusLote | None = Query(default=None, alias="status"),
) -> list[LoteListagemResponse]:
    service = LoteService(db)

    return service.listar_lotes(usuario_atual, offset, limit, status_lote)


@router.get("/arremates", status_code=200)
def listar_arremates(
    usuario_atual: Annotated[
        UsuarioResponse,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    service = LoteService(db)

    return service.buscar_lotes_arrematados(usuario_atual.id)


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
        return service.buscar_lote_por_id(lote_id)
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
    except LoteRegraNegocioError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
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
    except LoteRegraNegocioError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
