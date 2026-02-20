"""add_freshness_score_to_articles

Revision ID: 76c10cf3a634
Revises: 9e54cd9a6c4b
Create Date: 2026-01-10 16:26:20.527900

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "76c10cf3a634"
down_revision: Union[str, Sequence[str], None] = "9e54cd9a6c4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add freshness_score column after source, remove from quality_metrics."""
    # SQLite doesn't support ADD COLUMN in specific position, so recreate table
    op.execute(
        """
        CREATE TABLE articles_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            newsletter_id INTEGER NOT NULL,
            category VARCHAR(20) NOT NULL,
            source VARCHAR(100) NOT NULL,
            freshness_score FLOAT,
            quality_metrics TEXT NOT NULL DEFAULT '{"content_score": null, "relevance_score": null, "confidence": null}',
            ai_title TEXT NOT NULL,
            text TEXT,
            link VARCHAR(1000) NOT NULL,
            published_at DATETIME,
            fetched_at DATETIME NOT NULL,
            FOREIGN KEY (newsletter_id) REFERENCES newsletters(id) ON DELETE CASCADE
        )
        """
    )

    # Copy data, strip freshness_score from quality_metrics JSON
    op.execute(
        """
        INSERT INTO articles_new (id, newsletter_id, category, source, freshness_score, quality_metrics, ai_title, text, link, published_at, fetched_at)
        SELECT
            id,
            newsletter_id,
            category,
            source,
            NULL,
            json_remove(quality_metrics, '$.freshness_score'),
            ai_title,
            text,
            link,
            published_at,
            fetched_at
        FROM articles
        """
    )

    op.execute("DROP TABLE articles")
    op.execute("ALTER TABLE articles_new RENAME TO articles")

    # Recreate indexes
    op.execute("CREATE INDEX ix_articles_newsletter_id ON articles (newsletter_id)")
    op.execute("CREATE INDEX ix_articles_category ON articles (category)")
    op.execute("CREATE INDEX ix_articles_source ON articles (source)")


def downgrade() -> None:
    """Remove freshness_score column, add back to quality_metrics."""
    op.execute(
        """
        CREATE TABLE articles_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            newsletter_id INTEGER NOT NULL,
            category VARCHAR(20) NOT NULL,
            source VARCHAR(100) NOT NULL,
            quality_metrics TEXT NOT NULL DEFAULT '{"freshness_score": null, "content_score": null, "relevance_score": null, "confidence": null}',
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
        SELECT
            id,
            newsletter_id,
            category,
            source,
            quality_metrics,
            ai_title,
            text,
            link,
            published_at,
            fetched_at
        FROM articles
        """
    )

    op.execute("DROP TABLE articles")
    op.execute("ALTER TABLE articles_new RENAME TO articles")

    op.execute("CREATE INDEX ix_articles_newsletter_id ON articles (newsletter_id)")
    op.execute("CREATE INDEX ix_articles_category ON articles (category)")
    op.execute("CREATE INDEX ix_articles_source ON articles (source)")
