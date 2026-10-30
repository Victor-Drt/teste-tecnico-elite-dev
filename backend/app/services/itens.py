import httpx
from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.itens import ItensApiExterna, ItemResumo
from app.repositories import itens as repository

MAX_API_PAGE_SIZE = 100
MAX_API_SEARCH_RECORDS = 1000


class ItemService:
    def __init__(self, db: Session):
        self.db = db

    def listar_itens(
        self, offset: int, limit: int, query: str | None
    ) -> list[ItemResumo]:
        itens = repository.listar_itens(self.db, offset, limit, query)

        return [ItemResumo.model_validate(item) for item in itens]

    async def sincronizar_itens_api_externa(
        self, page: int = 1, limit: int = 10
    ) -> int:
        self._validar_paginacao_api_externa(page, limit)
        total_salvo = 0

        while True:
            itens_externos = await self.listar_itens_api_externa(page, limit)
            total_salvo += repository.salvar_ou_atualizar_itens(self.db, itens_externos)

            if len(itens_externos) < limit or page * limit >= MAX_API_SEARCH_RECORDS:
                return total_salvo

            page += 1

    async def listar_itens_api_externa(self, page: int, limit: int):
        self._validar_paginacao_api_externa(page, limit)

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

            # print(itens[0])

            return itens

    @staticmethod
    def _validar_paginacao_api_externa(page: int, limit: int) -> None:
        if page < 1:
            raise ValueError("A página deve ser maior ou igual a 1.")
        if limit < 1 or limit > MAX_API_PAGE_SIZE:
            raise ValueError(f"O limite deve estar entre 1 e {MAX_API_PAGE_SIZE}.")
        if page * limit > MAX_API_SEARCH_RECORDS:
            raise ValueError(
                "A busca não pode ultrapassar 1.000 registros "
                "considerando página e limite."
            )
