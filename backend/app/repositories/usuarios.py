from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuarios import Usuario


def criar_usuario(db: Session, usuario: Usuario) -> Usuario | None:

    query = select(Usuario).where(Usuario.email == usuario.email)
    usuario_existente = db.execute(query).scalar_one_or_none()

    if usuario_existente:
        return None

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
