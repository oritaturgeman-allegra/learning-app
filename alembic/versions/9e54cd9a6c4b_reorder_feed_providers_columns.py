"""reorder_feed_providers_columns

Revision ID: 9e54cd9a6c4b
Revises: e936df4bf7cf
Create Date: 2026-01-10 15:54:32.977555

Reorder columns so feed_url comes after source_name.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e54cd9a6c4b"
down_revision: Union[str, Sequence[str], None] = "e936df4bf7cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Recreate table with correct column order: feed_url after source_name."""
    # Create new table with correct column order
    op.create_table(
        "feed_providers_new",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("feed_url", sa.String(500), nullable=True),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False, default=0),
        sa.Column("total_runs", sa.Integer(), nullable=False, default=0),
        sa.Column("reliability", sa.Float(), nullable=False, default=0.0),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_name", "category", name="uq_feed_provider"),
    )

    # Copy data
    op.execute(
        """
        INSERT INTO feed_providers_new
            (id, source_name, feed_url, category, success_count, total_runs, reliability, last_updated)
        SELECT
            id, source_name, feed_url, category, success_count, total_runs, reliability, last_updated
        FROM feed_providers
    """
    )

    # Drop old table and rename
    op.drop_table("feed_providers")
    op.rename_table("feed_providers_new", "feed_providers")


def downgrade() -> None:
    """No-op - column order doesn't affect functionality."""
    pass
