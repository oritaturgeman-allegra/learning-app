"""Reorder newsletters columns - user_id after id

Revision ID: 0c744c3824d7
Revises: 1bfd219c01d9
Create Date: 2025-12-11 19:41:17.073139

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0c744c3824d7"
down_revision: Union[str, Sequence[str], None] = "1bfd219c01d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - recreate newsletters table with user_id after id."""
    # SQLite doesn't support column reordering, so we recreate the table manually

    # 1. Create new table with correct column order
    op.execute(
        """
        CREATE TABLE newsletters_new (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER,
            ai_market_summary TEXT,
            ai_podcast_dialog TEXT,
            language VARCHAR(5) NOT NULL DEFAULT 'en',
            audio_url VARCHAR(500),
            sentiment VARCHAR(50),
            llm_provider VARCHAR(50),
            tts_provider VARCHAR(50),
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """
    )

    # 2. Copy data from old table
    op.execute(
        """
        INSERT INTO newsletters_new (id, user_id, ai_market_summary, ai_podcast_dialog, language, audio_url, sentiment, llm_provider, tts_provider, created_at, updated_at)
        SELECT id, user_id, ai_market_summary, ai_podcast_dialog, language, audio_url, sentiment, llm_provider, tts_provider, created_at, updated_at
        FROM newsletters
    """
    )

    # 3. Drop old table
    op.execute("DROP TABLE newsletters")

    # 4. Rename new table
    op.execute("ALTER TABLE newsletters_new RENAME TO newsletters")

    # 5. Recreate index
    op.execute("CREATE INDEX ix_newsletters_user_id ON newsletters (user_id)")


def downgrade() -> None:
    """Downgrade schema - column order is cosmetic, no action needed."""
    pass
