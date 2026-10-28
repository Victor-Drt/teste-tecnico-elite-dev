from fastapi import APIRouter
from app.api.v1.endpoints.usuarios import router as usuario_router

api_router = APIRouter()


api_router.include_router(
    usuario_router,
    prefix="/usuarios",
    tags=["usuarios"],
)
