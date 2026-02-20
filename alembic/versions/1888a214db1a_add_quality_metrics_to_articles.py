"""add_quality_metrics_to_articles

Revision ID: 1888a214db1a
Revises: 81cfdbf9c201
Create Date: 2026-01-07 22:02:24.973421

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1888a214db1a"
down_revision: Union[str, Sequence[str], None] = "81cfdbf9c201"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("articles") as batch_op:
        batch_op.add_column(sa.Column("quality_metrics", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("articles") as batch_op:
        batch_op.drop_column("quality_metrics")
