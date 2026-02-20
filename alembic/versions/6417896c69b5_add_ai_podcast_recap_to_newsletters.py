"""Add ai_podcast_recap to newsletters

Revision ID: 6417896c69b5
Revises: 1c5c5c9fbb0a
Create Date: 2025-12-01 13:03:46.479927

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6417896c69b5"
down_revision: Union[str, Sequence[str], None] = "1c5c5c9fbb0a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ai_podcast_recap column to newsletters table."""
    op.add_column("newsletters", sa.Column("ai_podcast_recap", sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove ai_podcast_recap column from newsletters table."""
    op.drop_column("newsletters", "ai_podcast_recap")
