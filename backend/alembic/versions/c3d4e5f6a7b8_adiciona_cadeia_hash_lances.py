"""adiciona cadeia de hashes para auditoria de lances

Revision ID: c3d4e5f6a7b8
Revises: b2c4d6e8f010
Create Date: 2026-11-02 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c4d6e8f010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "lances",
        sa.Column("hash_anterior", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "lances",
        sa.Column("hash_evento", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "liquidacoes_lotes",
        sa.Column("hash_cadeia_lances", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "liquidacoes_lotes",
        sa.Column("quantidade_lances", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("liquidacoes_lotes", "quantidade_lances")
    op.drop_column("liquidacoes_lotes", "hash_cadeia_lances")
    op.drop_column("lances", "hash_evento")
    op.drop_column("lances", "hash_anterior")
