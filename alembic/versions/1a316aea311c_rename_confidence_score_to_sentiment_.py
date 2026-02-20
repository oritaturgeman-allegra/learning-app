"""Rename confidence_score to sentiment and title to ai_title

Revision ID: 1a316aea311c
Revises: 6a873169c45e
Create Date: 2025-11-30 12:56:01.323056

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1a316aea311c"
down_revision: Union[str, Sequence[str], None] = "6a873169c45e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename title to ai_title in articles
    op.add_column("articles", sa.Column("ai_title", sa.Text(), nullable=True))
    op.execute("UPDATE articles SET ai_title = title")
    op.drop_column("articles", "title")
    # Make ai_title NOT NULL after data migration (SQLite doesn't support ALTER COLUMN)

    # Rename confidence_score to sentiment in newsletters
    op.add_column("newsletters", sa.Column("sentiment", sa.String(length=50), nullable=True))
    # Note: confidence_score was a float, sentiment is a string - no data to migrate
    op.drop_column("newsletters", "confidence_score")


def downgrade() -> None:
    """Downgrade schema."""
    # Restore confidence_score
    op.add_column("newsletters", sa.Column("confidence_score", sa.FLOAT(), nullable=True))
    op.drop_column("newsletters", "sentiment")

    # Restore title from ai_title
    op.add_column("articles", sa.Column("title", sa.TEXT(), nullable=True))
    op.execute("UPDATE articles SET title = ai_title")
    op.drop_column("articles", "ai_title")
