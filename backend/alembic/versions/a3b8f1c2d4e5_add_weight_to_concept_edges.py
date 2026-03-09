"""add weight to concept edges

Revision ID: a3b8f1c2d4e5
Revises: 75ca77cca0fd
Create Date: 2026-03-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3b8f1c2d4e5"
down_revision: Union[str, None] = "75ca77cca0fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "question_evaluates",
        sa.Column("weight", sa.Float(), server_default="1.0", nullable=False),
    )
    op.add_column(
        "question_requires",
        sa.Column("weight", sa.Float(), server_default="1.0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("question_requires", "weight")
    op.drop_column("question_evaluates", "weight")
