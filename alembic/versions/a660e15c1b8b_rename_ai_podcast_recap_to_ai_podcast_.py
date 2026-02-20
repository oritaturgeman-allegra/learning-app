"""rename_ai_podcast_recap_to_ai_podcast_dialog

Revision ID: a660e15c1b8b
Revises: 6417896c69b5
Create Date: 2025-12-02 13:01:26.411510

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a660e15c1b8b"
down_revision: Union[str, Sequence[str], None] = "6417896c69b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename ai_podcast_recap to ai_podcast_dialog in newsletters table
    op.alter_column("newsletters", "ai_podcast_recap", new_column_name="ai_podcast_dialog")


def downgrade() -> None:
    """Downgrade schema."""
    # Revert: rename ai_podcast_dialog back to ai_podcast_recap
    op.alter_column("newsletters", "ai_podcast_dialog", new_column_name="ai_podcast_recap")
