"""add baseline_models table

Revision ID: b1c2d3e4f5a6
Revises: a3b8f1c2d4e5
Create Date: 2026-03-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'a3b8f1c2d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create baseline_models table."""
    op.create_table('baseline_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tuning_job_id', sa.String(length=500), nullable=False),
        sa.Column('model_endpoint', sa.String(length=500), nullable=True),
        sa.Column('model_name', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('pending', 'training', 'succeeded', 'failed', name='loramodelstatus', create_type=False), nullable=False),
        sa.Column('training_samples_count', sa.Integer(), nullable=False),
        sa.Column('dataset_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop baseline_models table."""
    op.drop_table('baseline_models')
