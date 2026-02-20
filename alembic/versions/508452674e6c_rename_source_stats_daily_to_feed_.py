"""rename_source_stats_daily_to_feed_providers

Revision ID: 508452674e6c
Revises: 1def8432385b
Create Date: 2026-01-08 13:08:02.645420

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "508452674e6c"
down_revision: Union[str, Sequence[str], None] = "1def8432385b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename source_stats_daily to feed_providers."""
    op.rename_table("source_stats_daily", "feed_providers")

    # Rename index
    op.drop_index("ix_source_stats_daily_date", table_name="feed_providers")
    op.create_index("ix_feed_providers_date", "feed_providers", ["stat_date"])

    # Rename unique constraint (SQLite: recreate table)
    op.execute(
        """
        CREATE TABLE feed_providers_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name VARCHAR(100) NOT NULL,
            category VARCHAR(20) NOT NULL,
            stat_date DATE NOT NULL,
            success_count INTEGER DEFAULT 0 NOT NULL,
            total_runs INTEGER DEFAULT 0 NOT NULL,
            reliability FLOAT DEFAULT 0.0 NOT NULL,
            last_article_count INTEGER DEFAULT 0 NOT NULL,
            CONSTRAINT uq_feed_provider_date UNIQUE (source_name, category, stat_date)
        )
        """
    )
    op.execute(
        """
        INSERT INTO feed_providers_new
        SELECT * FROM feed_providers
        """
    )
    op.drop_table("feed_providers")
    op.rename_table("feed_providers_new", "feed_providers")
    op.create_index("ix_feed_providers_date", "feed_providers", ["stat_date"])


def downgrade() -> None:
    """Rename feed_providers back to source_stats_daily."""
    op.rename_table("feed_providers", "source_stats_daily")

    # Rename index
    op.drop_index("ix_feed_providers_date", table_name="source_stats_daily")
    op.create_index("ix_source_stats_daily_date", "source_stats_daily", ["stat_date"])

    # Rename unique constraint back
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
    op.execute(
        """
        INSERT INTO source_stats_daily_new
        SELECT * FROM source_stats_daily
        """
    )
    op.drop_table("source_stats_daily")
    op.rename_table("source_stats_daily_new", "source_stats_daily")
    op.create_index("ix_source_stats_daily_date", "source_stats_daily", ["stat_date"])
