"""set_quality_metrics_default_not_null

Revision ID: 4361ddeb78b7
Revises: a1d4efb3e9a8
Create Date: 2026-01-07 22:09:13.212866

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4361ddeb78b7"
down_revision: Union[str, Sequence[str], None] = "a1d4efb3e9a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_QUALITY_METRICS = '{"freshness_score": null, "content_score": null, "source_reliability": null, "relevance_score": null, "confidence": null}'


def upgrade() -> None:
    """Upgrade schema - set default value for existing rows and make NOT NULL."""
    # Update existing NULL rows with default value
    op.execute(
        f"UPDATE articles SET quality_metrics = '{DEFAULT_QUALITY_METRICS}' WHERE quality_metrics IS NULL"
    )

    # Recreate table with NOT NULL constraint
    op.execute(
        f"""
        CREATE TABLE articles_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            newsletter_id INTEGER NOT NULL,
            category VARCHAR(20) NOT NULL,
            source VARCHAR(100) NOT NULL,
            quality_metrics TEXT NOT NULL DEFAULT '{DEFAULT_QUALITY_METRICS}',
            ai_title TEXT NOT NULL,
            text TEXT,
            link VARCHAR(1000) NOT NULL,
            published_at DATETIME,
            fetched_at DATETIME NOT NULL,
            FOREIGN KEY (newsletter_id) REFERENCES newsletters(id) ON DELETE CASCADE
        )
    """
    )

    op.execute(
        """
        INSERT INTO articles_new (id, newsletter_id, category, source, quality_metrics, ai_title, text, link, published_at, fetched_at)
        SELECT id, newsletter_id, category, source, quality_metrics, ai_title, text, link, published_at, fetched_at
        FROM articles
    """
    )

    op.execute("DROP TABLE articles")
    op.execute("ALTER TABLE articles_new RENAME TO articles")

    op.execute("CREATE INDEX ix_articles_newsletter_id ON articles (newsletter_id)")
    op.execute("CREATE INDEX ix_articles_category ON articles (category)")
    op.execute("CREATE INDEX ix_articles_source ON articles (source)")


def downgrade() -> None:
    """Downgrade schema - make quality_metrics nullable again."""
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

    op.execute(
        """
        INSERT INTO articles_new (id, newsletter_id, category, source, quality_metrics, ai_title, text, link, published_at, fetched_at)
        SELECT id, newsletter_id, category, source, quality_metrics, ai_title, text, link, published_at, fetched_at
        FROM articles
    """
    )

    op.execute("DROP TABLE articles")
    op.execute("ALTER TABLE articles_new RENAME TO articles")

    op.execute("CREATE INDEX ix_articles_newsletter_id ON articles (newsletter_id)")
    op.execute("CREATE INDEX ix_articles_category ON articles (category)")
    op.execute("CREATE INDEX ix_articles_source ON articles (source)")
