from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, Token
from app.services.auth import AuthService


router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    data: LoginRequest, db: Session = Depends(get_db)
) -> Token:
    
    try:
        service = AuthService(db)
        access_token = service.authenticate_user(data)
        
        return Token(access_token=access_token, token_type="bearer")

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )
