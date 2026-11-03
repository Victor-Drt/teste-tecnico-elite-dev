from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, Token
from app.services.auth import AuthService
from app.core.config import settings


router = APIRouter()


@router.post("/token", summary="Autentica e cria a sessão do usuário")
async def login_for_access_token(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> Token:
    try:
        service = AuthService(db)
        access_token = service.authenticate_user(data)

        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
        )

        return Token(access_token=access_token, token_type="bearer")

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post("/logout", summary="Encerra a sessão do usuário")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Logout realizado"}