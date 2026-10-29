from fastapi import APIRouter
from app.api.v1.endpoints.usuarios import router as usuario_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.itens import router as item_router

api_router = APIRouter()


api_router.include_router(
    usuario_router,
    prefix="/usuarios",
    tags=["Usuarios"],
)
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(item_router, prefix="/itens", tags=["Item"])
