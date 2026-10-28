from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.usuarios import PapelUsuario


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    senha: str
    papel: PapelUsuario


class UsuarioResponse(UsuarioBase):
    id: int
    papel: PapelUsuario

    model_config = ConfigDict(from_attributes=True)
