"""add_cached_column_to_podcast_generations

Revision ID: 58af40a74233
Revises: d925b89e968d
Create Date: 2026-02-10 14:46:02.284198

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "58af40a74233"
down_revision: Union[str, Sequence[str], None] = "d925b89e968d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cached column to podcast_generations table."""
    op.add_column(
        "podcast_generations",
        sa.Column("cached", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Remove cached column from podcast_generations table."""
    op.drop_column("podcast_generations", "cached")
