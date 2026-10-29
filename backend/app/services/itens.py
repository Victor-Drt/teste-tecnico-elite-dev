import httpx
from typing import List
from pydantic import TypeAdapter

from app.core.config import settings
from app.schemas.itens import ItensApiExterna


class ItemService:
    def __init__(self, db):
        self.db = db

    async def listar_itens(self, page: int = 1, limit: int = 10):

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

            dados_itens = response.json()["data"]

            adapter = TypeAdapter(List[ItensApiExterna])
            itens: List[ItensApiExterna] = adapter.validate_python(dados_itens)

            return itens
