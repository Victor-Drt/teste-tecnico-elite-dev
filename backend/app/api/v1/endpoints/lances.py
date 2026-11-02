from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.api.v1.deps import get_current_user, verificar_role
from app.db.session import get_db
from app.schemas.usuarios import UsuarioResponse
from app.schemas.lances import (
    CategoriaMeusLances,
    HistoricoLancesPagina,
    LanceCreate,
    LanceResumo,
    MeuLancePagina,
)
from app.services.lances import LanceService
from app.api.v1.websockets.leiloes import notificar_lance_criado

router = APIRouter()


@router.get("/meus", status_code=200, response_model=MeuLancePagina)
def listar_meus_lances(
    usuario_atual: Annotated[
        UsuarioResponse, Depends(verificar_role("licitante"))
    ],
    categoria: CategoriaMeusLances = Query(
        default=CategoriaMeusLances.MEUS_LANCES
    ),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> MeuLancePagina:
    service = LanceService(db)
    return service.listar_meus_lances(
        usuario_atual.id, categoria, offset, limit
    )


@router.get("/lotes/{lote_id}", status_code=200)
def listar_lances(
    lote_id: int,
    db: Session = Depends(get_db),
) -> list[LanceResumo]:
    service = LanceService(db)

    return service.listar_lances_por_lote(lote_id)


@router.get(
    "/lotes/{lote_id}/historico",
    status_code=200,
    response_model=HistoricoLancesPagina,
)
def listar_historico_lances(
    lote_id: int,
    usuario_atual: Annotated[
        UsuarioResponse, Depends(verificar_role("licitante"))
    ],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> HistoricoLancesPagina:
    service = LanceService(db)
    return service.listar_historico_lances(
        lote_id, usuario_atual.id, offset, limit
    )


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
async def criar_lance(
    data: LanceCreate,
    usuario_atual: Annotated[UsuarioResponse, Depends(verificar_role("licitante"))],
    db: Session = Depends(get_db),
) -> LanceResumo:
    service = LanceService(db)

    try:
        lance = service.criar_lance(usuario_atual, data)
        await notificar_lance_criado(lance, db)
        return lance
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
