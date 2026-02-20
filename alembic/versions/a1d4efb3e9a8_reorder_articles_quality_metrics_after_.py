"""reorder_articles_quality_metrics_after_source

Revision ID: a1d4efb3e9a8
Revises: 1888a214db1a
Create Date: 2026-01-07 22:05:33.554030

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a1d4efb3e9a8"
down_revision: Union[str, Sequence[str], None] = "1888a214db1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - reorder columns with quality_metrics after source."""
    # Create new table with correct column order
    op.execute(
        """
        CREATE TABLE articles_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            newsletter_id INTEGER NOT NULL,
            category VARCHAR(20) NOT NULL,
            source VARCHAR(100) NOT NULL,
            quality_metrics TEXT,
            ai_title TEXT NOT NULL,
            text TEXT,
            link VARCHAR(1000) NOT NULL,
            published_at DATETIME,
            fetched_at DATETIME NOT NULL,
            FOREIGN KEY (newsletter_id) REFERENCES newsletters(id) ON DELETE CASCADE
        )
    """
    )

    # Copy data
    op.execute(
        """
        INSERT INTO articles_new (id, newsletter_id, category, source, quality_metrics, ai_title, text, link, published_at, fetched_at)
        SELECT id, newsletter_id, category, source, quality_metrics, ai_title, text, link, published_at, fetched_at
        FROM articles
    """
    )

    # Drop old table and rename new one
    op.execute("DROP TABLE articles")
    op.execute("ALTER TABLE articles_new RENAME TO articles")

    # Recreate indexes
    op.execute("CREATE INDEX ix_articles_newsletter_id ON articles (newsletter_id)")
    op.execute("CREATE INDEX ix_articles_category ON articles (category)")
    op.execute("CREATE INDEX ix_articles_source ON articles (source)")


def downgrade() -> None:
    """Downgrade schema - move quality_metrics back to end."""
    op.execute(
        """
        CREATE TABLE articles_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            newsletter_id INTEGER NOT NULL,
            category VARCHAR(20) NOT NULL,
            source VARCHAR(100) NOT NULL,
            ai_title TEXT NOT NULL,
            text TEXT,
            link VARCHAR(1000) NOT NULL,
            published_at DATETIME,
            fetched_at DATETIME NOT NULL,
            quality_metrics TEXT,
            FOREIGN KEY (newsletter_id) REFERENCES newsletters(id) ON DELETE CASCADE
        )
    """
    )

    op.execute(
        """
        INSERT INTO articles_new (id, newsletter_id, category, source, ai_title, text, link, published_at, fetched_at, quality_metrics)
        SELECT id, newsletter_id, category, source, ai_title, text, link, published_at, fetched_at, quality_metrics
        FROM articles
    """
    )

    op.execute("DROP TABLE articles")
    op.execute("ALTER TABLE articles_new RENAME TO articles")

    op.execute("CREATE INDEX ix_articles_newsletter_id ON articles (newsletter_id)")
    op.execute("CREATE INDEX ix_articles_category ON articles (category)")
    op.execute("CREATE INDEX ix_articles_source ON articles (source)")
