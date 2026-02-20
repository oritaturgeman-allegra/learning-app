"""reorder_podcast_generations_columns

Revision ID: d40834a43c1c
Revises: 58af40a74233
Create Date: 2026-02-10 14:54:50.812876

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d40834a43c1c"
down_revision: Union[str, Sequence[str], None] = "58af40a74233"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Reorder columns: move 'cached' after 'categories'."""
    # SQLite doesn't support column reordering, so we recreate the table
    op.execute(
        """
        CREATE TABLE podcast_generations_new (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            categories TEXT NOT NULL,
            cached BOOLEAN NOT NULL DEFAULT 0,
            cache_key VARCHAR(64) NOT NULL,
            created_at DATETIME NOT NULL
        )
    """
    )
    op.execute(
        """
        INSERT INTO podcast_generations_new (id, user_id, categories, cached, cache_key, created_at)
        SELECT id, user_id, categories, cached, cache_key, created_at FROM podcast_generations
    """
    )
    op.execute("DROP TABLE podcast_generations")
    op.execute("ALTER TABLE podcast_generations_new RENAME TO podcast_generations")
    op.execute("CREATE INDEX ix_podcast_generations_user_id ON podcast_generations (user_id)")


def downgrade() -> None:
    """Move 'cached' back to end of table."""
    op.execute(
        """
        CREATE TABLE podcast_generations_new (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            categories TEXT NOT NULL,
            cache_key VARCHAR(64) NOT NULL,
            created_at DATETIME NOT NULL,
            cached BOOLEAN NOT NULL DEFAULT 0
        )
    """
    )
    op.execute(
        """
        INSERT INTO podcast_generations_new (id, user_id, categories, cache_key, created_at, cached)
        SELECT id, user_id, categories, cache_key, created_at, cached FROM podcast_generations
    """
    )
    op.execute("DROP TABLE podcast_generations")
    op.execute("ALTER TABLE podcast_generations_new RENAME TO podcast_generations")
    op.execute("CREATE INDEX ix_podcast_generations_user_id ON podcast_generations (user_id)")
