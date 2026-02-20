"""simplify_feed_providers_table

Revision ID: 036b4b57524f
Revises: 508452674e6c
Create Date: 2026-01-08 13:17:16.181411

Aggregates daily stats into lifetime stats per provider.
Removes stat_date and last_article_count columns.
Adds last_updated column.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "036b4b57524f"
down_revision: Union[str, Sequence[str], None] = "508452674e6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: aggregate daily stats into lifetime stats."""
    # SQLite doesn't support dropping columns directly, so we recreate the table

    # 1. Create new table with simplified structure
    op.create_table(
        "feed_providers_new",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False, default=0),
        sa.Column("total_runs", sa.Integer(), nullable=False, default=0),
        sa.Column("reliability", sa.Float(), nullable=False, default=0.0),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_name", "category", name="uq_feed_provider"),
    )

    # 2. Aggregate and migrate data from old table
    # Sum success_count and total_runs per provider, recalculate reliability
    op.execute(
        """
        INSERT INTO feed_providers_new (source_name, category, success_count, total_runs, reliability, last_updated)
        SELECT
            source_name,
            category,
            SUM(success_count) as success_count,
            SUM(total_runs) as total_runs,
            CASE
                WHEN SUM(total_runs) > 0 THEN CAST(SUM(success_count) AS REAL) / SUM(total_runs)
                ELSE 0.0
            END as reliability,
            MAX(stat_date) as last_updated
        FROM feed_providers
        GROUP BY source_name, category
    """
    )

    # 3. Drop old table
    op.drop_table("feed_providers")

    # 4. Rename new table
    op.rename_table("feed_providers_new", "feed_providers")


def downgrade() -> None:
    """Downgrade schema: cannot restore daily granularity, just recreate structure."""
    # Note: We cannot restore the original daily granularity since data was aggregated
    # This downgrade just recreates the old schema structure

    op.create_table(
        "feed_providers_old",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("stat_date", sa.Date(), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False, default=0),
        sa.Column("total_runs", sa.Integer(), nullable=False, default=0),
        sa.Column("last_article_count", sa.Integer(), nullable=False, default=0),
        sa.Column("reliability", sa.Float(), nullable=False, default=0.0),
        sa.UniqueConstraint("source_name", "category", "stat_date", name="uq_source_stat_daily"),
    )

    # Migrate data back (as single day entries using last_updated as stat_date)
    op.execute(
        """
        INSERT INTO feed_providers_old (source_name, category, stat_date, success_count, total_runs, last_article_count, reliability)
        SELECT
            source_name,
            category,
            DATE(last_updated) as stat_date,
            success_count,
            total_runs,
            0 as last_article_count,
            reliability
        FROM feed_providers
    """
    )

    op.drop_table("feed_providers")
    op.rename_table("feed_providers_old", "feed_providers")
