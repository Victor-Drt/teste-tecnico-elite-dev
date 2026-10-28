from sqlalchemy.orm import Session
from datetime import timedelta

from app.schemas.auth import LoginRequest, Token
from app.repositories import usuarios as repository
from app.core.security import verify_password, create_access_token
from app.core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, data: LoginRequest) -> str:

        usuario = repository.get_usuario_by_email(self.db, data.email)

        if usuario is None:
            raise ValueError("E-mail ou senha incorretos")

        if not verify_password(data.senha, usuario.senha):
            raise ValueError("E-mail ou senha incorretos")

        access_token_expires = timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        access_token = create_access_token(
            data={"sub": usuario.email}, expires_delta=access_token_expires
        )

        return access_token
