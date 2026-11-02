"""adiciona comprovante de liquidacao e indice para encerramento

Revision ID: b2c4d6e8f010
Revises: 66a355d978ce
Create Date: 2026-11-02 12:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c4d6e8f010"
down_revision: Union[str, Sequence[str], None] = "66a355d978ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "carteiras",
        "saldo_total",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.Numeric(precision=14, scale=2),
        existing_nullable=False,
    )
    op.alter_column(
        "carteiras",
        "saldo_comprometido",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.Numeric(precision=14, scale=2),
        existing_nullable=False,
    )
    op.create_index(
        "ix_lotes_status_data_fim",
        "lotes",
        ["status", "data_fim"],
        unique=False,
    )
    op.create_table(
        "liquidacoes_lotes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lote_id", sa.Integer(), nullable=False),
        sa.Column("leiloeiro_id", sa.Integer(), nullable=False),
        sa.Column("vencedor_id", sa.Integer(), nullable=True),
        sa.Column("lance_id", sa.Integer(), nullable=True),
        sa.Column("valor", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "data_liquidacao",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["lance_id"], ["lances.id"]),
        sa.ForeignKeyConstraint(["leiloeiro_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["lote_id"], ["lotes.id"]),
        sa.ForeignKeyConstraint(["vencedor_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lote_id", name="uq_liquidacoes_lotes_lote_id"),
    )


def downgrade() -> None:
    op.drop_table("liquidacoes_lotes")
    op.drop_index("ix_lotes_status_data_fim", table_name="lotes")
    op.alter_column(
        "carteiras",
        "saldo_comprometido",
        existing_type=sa.Numeric(precision=14, scale=2),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False,
    )
    op.alter_column(
        "carteiras",
        "saldo_total",
        existing_type=sa.Numeric(precision=14, scale=2),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False,
    )
