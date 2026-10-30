import asyncio
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.itens import ItemService

logger = logging.getLogger(__name__)


async def sincronizar_uma_vez() -> None:
    with SessionLocal() as db:
        quantidade = await ItemService(db).sincronizar_itens_api_externa()

    logger.info("Sincronização concluída: %s itens processados.", quantidade)


async def executar_ciclo() -> None:
    try:
        await sincronizar_uma_vez()
    except Exception:
        logger.exception("Falha ao sincronizar itens; os dados locais foram mantidos.")


async def executar_agendador() -> None:
    while True:
        await executar_ciclo()
        await asyncio.sleep(settings.SYNC_ITENS_INTERVAL_SECONDS)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(executar_agendador())


if __name__ == "__main__":
    main()
