from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.usuarios import UsuarioResponse
from app.models.lotes import StatusLote
from app.schemas.lotes import (
    AuditoriaPublicaResponse,
    ComprovanteArremateResponse,
    LoteCreate,
    LoteDetalhesResponse,
    LoteListagemResponse,
    LoteUpdate,
    LoteVitrineResponse,
)
from app.api.v1.deps import verificar_role, get_current_user
from app.db.session import get_db
from app.services.lotes import (
    AuditoriaPublicaInconsistente,
    ComprovanteArremateInconsistente,
    LoteRegraNegocioError,
    LoteService,
)

router = APIRouter()


@router.post(
    "/",
    status_code=201,
    summary="Cria um lote de leilão",
)
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


@router.get("/", status_code=200, summary="Lista lotes disponíveis")
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


@router.get(
    "/arremates",
    status_code=200,
    summary="Lista os lotes arrematados pelo usuário",
)
def listar_arremates(
    usuario_atual: Annotated[
        UsuarioResponse,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    service = LoteService(db)

    return service.buscar_lotes_arrematados(usuario_atual.id)


@router.get(
    "/{lote_id}/vitrine",
    status_code=200,
    response_model=LoteVitrineResponse,
    summary="Consulta os dados de um lote para o leilão ao vivo",
)
def buscar_lote_para_vitrine(
    lote_id: int,
    usuario_atual: Annotated[
        UsuarioResponse,
        Depends(verificar_role("licitante")),
    ],
    db: Session = Depends(get_db),
) -> LoteVitrineResponse:
    service = LoteService(db)

    try:
        return service.buscar_lote_para_vitrine(lote_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{lote_id}/auditoria",
    status_code=200,
    response_model=AuditoriaPublicaResponse,
    summary="Verifica e consulta a auditoria pública do lote",
)
def buscar_auditoria_publica(
    lote_id: int,
    db: Session = Depends(get_db),
) -> AuditoriaPublicaResponse:
    service = LoteService(db)

    try:
        return service.buscar_auditoria_publica(lote_id)
    except AuditoriaPublicaInconsistente as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{lote_id}/comprovante",
    status_code=200,
    response_model=ComprovanteArremateResponse,
    summary="Consulta o comprovante de arremate do vencedor",
)
def buscar_comprovante_arremate(
    lote_id: int,
    usuario_atual: Annotated[
        UsuarioResponse, Depends(verificar_role("licitante"))
    ],
    db: Session = Depends(get_db),
) -> ComprovanteArremateResponse:
    service = LoteService(db)

    try:
        return service.buscar_comprovante_arremate(lote_id, usuario_atual.id)
    except ComprovanteArremateInconsistente as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{lote_id}",
    status_code=200,
    summary="Consulta os detalhes de um lote",
)
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


@router.patch(
    "/{lote_id}",
    status_code=200,
    summary="Atualiza os dados de um lote",
)
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


@router.delete(
    "/{lote_id}",
    status_code=204,
    summary="Remove um lote sem lances",
)
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
