"""Update sentiment to TEXT and reorder after user_id

Revision ID: b2088bf7a2d6
Revises: 0c744c3824d7
Create Date: 2025-12-24 16:42:33.907139

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b2088bf7a2d6"
down_revision: Union[str, Sequence[str], None] = "0c744c3824d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - change sentiment to TEXT and move after user_id."""
    # SQLite doesn't support ALTER COLUMN, so we recreate the table

    # 1. Create new table with correct column order and types
    op.execute(
        """
        CREATE TABLE newsletters_new (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER,
            sentiment TEXT,
            ai_market_summary TEXT,
            ai_podcast_dialog TEXT,
            language VARCHAR(5) NOT NULL DEFAULT 'en',
            audio_url VARCHAR(500),
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
        INSERT INTO newsletters_new (id, user_id, sentiment, ai_market_summary, ai_podcast_dialog, language, audio_url, llm_provider, tts_provider, created_at, updated_at)
        SELECT id, user_id, sentiment, ai_market_summary, ai_podcast_dialog, language, audio_url, llm_provider, tts_provider, created_at, updated_at
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
    """Downgrade schema - revert sentiment to VARCHAR(50) and move back."""
    # 1. Create old table structure
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

    # 2. Copy data (truncate sentiment if too long for VARCHAR(50))
    op.execute(
        """
        INSERT INTO newsletters_new (id, user_id, ai_market_summary, ai_podcast_dialog, language, audio_url, sentiment, llm_provider, tts_provider, created_at, updated_at)
        SELECT id, user_id, ai_market_summary, ai_podcast_dialog, language, audio_url, SUBSTR(sentiment, 1, 50), llm_provider, tts_provider, created_at, updated_at
        FROM newsletters
    """
    )

    # 3. Drop old table
    op.execute("DROP TABLE newsletters")

    # 4. Rename new table
    op.execute("ALTER TABLE newsletters_new RENAME TO newsletters")

    # 5. Recreate index
    op.execute("CREATE INDEX ix_newsletters_user_id ON newsletters (user_id)")
