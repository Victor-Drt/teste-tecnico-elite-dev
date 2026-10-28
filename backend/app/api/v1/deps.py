from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import TokenData
from app.core.config import settings
from app.repositories import usuarios as repository
from app.schemas.usuarios import UsuarioResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception

    user_dict = repository.get_usuario_by_email(db, token_data.email)
    if user_dict is None:
        raise credentials_exception
    return UsuarioResponse(
        id=user_dict.id,
        nome=user_dict.nome,
        email=user_dict.email,
        papel=user_dict.papel,
    )
