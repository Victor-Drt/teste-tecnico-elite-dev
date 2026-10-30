import httpx
from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.itens import ItensApiExterna, ItemResumo
from app.repositories import itens as repository


class ItemService:
    def __init__(self, db: Session):
        self.db = db

    def listar_itens(self, offset: int, limit: int) -> list[ItemResumo]:
        itens = repository.listar_itens(self.db, offset, limit)

        return [ItemResumo.model_validate(item) for item in itens]

    async def sincronizar_itens_api_externa(
        self, page: int = 1, limit: int = 10
    ) -> int:
        itens_externos = await self.listar_itens_api_externa(page, limit)
        return repository.salvar_ou_atualizar_itens(self.db, itens_externos)

    async def listar_itens_api_externa(self, page: int = 1, limit: int = 10):

        url = settings.API_EXTERNA_URL + f"&page={page}&limit={limit}"

        headers = {
            "User-Agent": "DesafioEliteDev/1.0",
            "AIC-User-Agent": "DesafioEliteDev/1.0",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                url,
                headers=headers,
            )

            response.raise_for_status()

            dados_itens = response.json()["data"]

            adapter = TypeAdapter(list[ItensApiExterna])
            itens: list[ItensApiExterna] = adapter.validate_python(dados_itens)

            return itens
