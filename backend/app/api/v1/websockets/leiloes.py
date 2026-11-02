import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from sqlalchemy.orm import Session

from app.api.v1.deps import validar_usuario
from app.db.session import get_db
from app.schemas.lances import LancePublico, LanceResumo
from app.schemas.usuarios import UsuarioResponse
from app.services.lances import LanceService
from app.services.lotes import LoteService
from app.services.cadeia_lances import mapear_participantes
from app.websockets.manage import connection_manager

logger = logging.getLogger(__name__)
router = APIRouter()


def _listar_participantes(
    lances: list[LanceResumo],
    aliases: dict[int, str],
) -> list[dict[str, int | str]]:
    melhores_lances: dict[int, LanceResumo] = {}
    for lance in sorted(lances, key=lambda item: (-item.valor, item.id)):
        melhores_lances.setdefault(lance.licitante_id, lance)

    participantes = sorted(
        melhores_lances.items(),
        key=lambda item: (-item[1].valor, item[1].id),
    )
    return [
        {
            "participante": aliases[licitante_id],
            "posicao": posicao,
            "situacao": "ganhando" if posicao == 1 else "superado",
        }
        for posicao, (licitante_id, _) in enumerate(participantes, start=1)
    ]


def _estado_usuario(
    participantes: list[dict[str, int | str]], participante_usuario: str | None
) -> dict[str, int | str | None]:
    participante = next(
        (
            participante
            for participante in participantes
            if participante["participante"] == participante_usuario
        ),
        None,
    )
    if participante is None or participante_usuario is None:
        return {
            "participante": None,
            "posicao": None,
            "situacao": "sem_lance",
        }

    return {
        "participante": participante_usuario,
        "posicao": participante["posicao"],
        "situacao": participante["situacao"],
    }


def _lance_para_json(
    lance: LanceResumo | None,
    aliases: dict[int, str],
) -> dict | None:
    if lance is None:
        return None
    return LancePublico(
        id=lance.id,
        participante=aliases[lance.licitante_id],
        lote_id=lance.lote_id,
        valor=lance.valor,
        data_criacao=lance.data_criacao,
    ).model_dump(mode="json")


async def notificar_lance_criado(
    lance: LanceResumo,
    db: Session,
) -> None:
    lances = LanceService(db).listar_lances_por_lote(lance.lote_id)
    aliases = mapear_participantes(lances)
    participantes = _listar_participantes(lances, aliases)
    lance_atual = lances[0] if lances else None
    lote = LoteService(db).buscar_lote_por_id(lance.lote_id)

    await connection_manager.broadcast(
        lance.lote_id,
        {
            "tipo": "lance_atualizado",
            "lote_id": lance.lote_id,
            "lance": _lance_para_json(lance, aliases),
            "lance_atual": _lance_para_json(lance_atual, aliases),
            "valor_atual": str(lote.valor_atual),
            "data_fim": lote.data_fim.isoformat(),
            "participantes": participantes,
        },
    )


async def autenticar_websocket(
    websocket: WebSocket,
    db: Annotated[Session, Depends(get_db)],
) -> UsuarioResponse:
    access_token = websocket.cookies.get("access_token")
    if not access_token:
        raise WebSocketException(code=1008, reason="Não autenticado")

    try:
        return validar_usuario(access_token, db)
    except HTTPException as exc:
        raise WebSocketException(code=1008, reason="Não autenticado") from exc


@router.websocket("/leilao/{lote_id}")
async def sala_de_leilao(
    lote_id: int,
    websocket: WebSocket,
    usuario: Annotated[UsuarioResponse, Depends(autenticar_websocket)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        lote = LoteService(db).buscar_lote_ao_vivo(lote_id)
    except ValueError:
        await websocket.close(code=1008, reason="Lote indisponível")
        return

    lances = LanceService(db).listar_lances_por_lote(lote_id)
    aliases = mapear_participantes(lances)
    participantes = _listar_participantes(lances, aliases)
    evento_inicial = {
        "tipo": "sala_inicial",
        "lote": {
            "id": lote.id,
            "status": lote.status.value,
            "data_fim": lote.data_fim.isoformat(),
            "valor_atual": str(lote.valor_atual),
        },
        "lance_atual": _lance_para_json(
            lances[0] if lances else None, aliases
        ),
        "historico_lances": [
            _lance_para_json(lance, aliases) for lance in lances
        ],
        "participantes": participantes,
        "usuario": _estado_usuario(
            participantes, aliases.get(usuario.id)
        ),
    }
    db.close()
    await connection_manager.connect(lote_id, websocket)

    try:
        await websocket.send_json(evento_inicial)

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(
            "Usuário %s desconectou da sala do lote %s",
            usuario.id,
            lote_id,
        )
    except (OSError, RuntimeError):
        logger.warning(
            "Conexão WebSocket interrompida para o usuário %s no lote %s",
            usuario.id,
            lote_id,
            exc_info=True,
        )
    finally:
        connection_manager.disconnect(lote_id, websocket)
