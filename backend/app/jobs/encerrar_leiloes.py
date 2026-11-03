import asyncio
import logging
from datetime import datetime

from app.core.config import settings
from app.core.time import utc_now_naive
from app.db.session import SessionLocal
from app.repositories import lotes as lote_repository
from app.services.lotes import LoteService

logger = logging.getLogger(__name__)
MAX_LOTES_POR_CICLO = 100


def encerrar_lotes_expirados_uma_vez() -> list[int]:
    agora = utc_now_naive()
    with SessionLocal() as db:
        lote_ids = lote_repository.listar_lotes_expirados(
            db, agora, MAX_LOTES_POR_CICLO
        )

    lotes_encerrados: list[int] = []
    for lote_id in lote_ids:
        try:
            with SessionLocal() as db:
                resultado = LoteService(db).encerrar_lote_expirado(lote_id, agora)
        except Exception:
            logger.exception(
                "Falha ao encerrar e liquidar o lote expirado %s.",
                lote_id,
            )
            continue

        if resultado is not None:
            lotes_encerrados.append(lote_id)
            logger.info(
                "Lote %s concluído; vencedor=%s, valor liquidado=%s.",
                resultado.lote_id,
                resultado.vencedor_id,
                resultado.valor_liquidado,
            )

    return lotes_encerrados


def ativar_lotes_agendados_uma_vez() -> list[int]:
    agora = utc_now_naive()
    with SessionLocal() as db:
        lote_ids = lote_repository.ativar_lotes_agendados(
            db, agora, MAX_LOTES_POR_CICLO
        )

    for lote_id in lote_ids:
        logger.info("Lote %s entrou ao vivo.", lote_id)

    return lote_ids


async def executar_ciclo() -> None:
    try:
        await asyncio.to_thread(ativar_lotes_agendados_uma_vez)
    except Exception:
        logger.exception("Falha ao ativar os leilões agendados.")

    try:
        await asyncio.to_thread(encerrar_lotes_expirados_uma_vez)
    except Exception:
        logger.exception("Falha ao verificar os leilões expirados.")


async def executar_agendador() -> None:
    while True:
        await executar_ciclo()
        await asyncio.sleep(settings.AUCTION_CLOSE_CHECK_INTERVAL_SECONDS)
