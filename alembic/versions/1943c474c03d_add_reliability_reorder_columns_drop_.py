"""add_reliability_reorder_columns_drop_source_stats

Revision ID: 1943c474c03d
Revises: 3330d9a9d6f7
Create Date: 2026-01-07 23:21:56.713432

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1943c474c03d"
down_revision: Union[str, Sequence[str], None] = "3330d9a9d6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Recreate source_stats_daily with new column order and reliability
    # Create new table with correct column order
    op.execute(
        """
        CREATE TABLE source_stats_daily_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name VARCHAR(100) NOT NULL,
            category VARCHAR(20) NOT NULL,
            stat_date DATE NOT NULL,
            success_count INTEGER DEFAULT 0 NOT NULL,
            total_runs INTEGER DEFAULT 0 NOT NULL,
            reliability FLOAT DEFAULT 0.0 NOT NULL,
            last_article_count INTEGER DEFAULT 0 NOT NULL,
            CONSTRAINT uq_source_category_date UNIQUE (source_name, category, stat_date)
        )
    """
    )

    # Copy data, calculating reliability from existing data
    op.execute(
        """
        INSERT INTO source_stats_daily_new
            (id, source_name, category, stat_date, success_count, total_runs, reliability, last_article_count)
        SELECT
            id, source_name, category, stat_date, success_count, total_runs,
            CASE WHEN total_runs > 0 THEN CAST(success_count AS FLOAT) / total_runs ELSE 0.0 END,
            last_article_count
        FROM source_stats_daily
    """
    )

    # Drop old table and rename new one
    op.drop_table("source_stats_daily")
    op.rename_table("source_stats_daily_new", "source_stats_daily")

    # Recreate index
    op.create_index("ix_source_stats_daily_date", "source_stats_daily", ["stat_date"])

    # 2. Drop source_stats table
    op.drop_table("source_stats")


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Recreate source_stats table
    op.create_table(
        "source_stats",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "newsletter_id",
            sa.Integer(),
            sa.ForeignKey("newsletters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("article_count", sa.Integer(), default=0),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_stats_newsletter_id", "source_stats", ["newsletter_id"])
    op.create_index("ix_source_stats_created_at", "source_stats", ["created_at"])

    # 2. Recreate source_stats_daily with old column order (without reliability)
    op.execute(
        """
        CREATE TABLE source_stats_daily_old (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name VARCHAR(100) NOT NULL,
            category VARCHAR(20) NOT NULL,
            stat_date DATE NOT NULL,
            total_runs INTEGER DEFAULT 0 NOT NULL,
            last_article_count INTEGER DEFAULT 0 NOT NULL,
            success_count INTEGER DEFAULT 0 NOT NULL,
            CONSTRAINT uq_source_category_date UNIQUE (source_name, category, stat_date)
        )
    """
    )

    op.execute(
        """
        INSERT INTO source_stats_daily_old
            (id, source_name, category, stat_date, total_runs, last_article_count, success_count)
        SELECT id, source_name, category, stat_date, total_runs, last_article_count, success_count
        FROM source_stats_daily
    """
    )

    op.drop_table("source_stats_daily")
    op.rename_table("source_stats_daily_old", "source_stats_daily")
    op.create_index("ix_source_stats_daily_date", "source_stats_daily", ["stat_date"])
