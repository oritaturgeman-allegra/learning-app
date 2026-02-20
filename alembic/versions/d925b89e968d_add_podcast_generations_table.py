"""add podcast_generations table

Revision ID: d925b89e968d
Revises: a9bcdd019a5d
Create Date: 2026-02-03 18:48:46.032876

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d925b89e968d"
down_revision: Union[str, Sequence[str], None] = "a9bcdd019a5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "podcast_generations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("categories", sa.Text(), nullable=False),
        sa.Column("cache_key", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("podcast_generations", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_podcast_generations_user_id"), ["user_id"], unique=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("podcast_generations", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_podcast_generations_user_id"))

    op.drop_table("podcast_generations")
