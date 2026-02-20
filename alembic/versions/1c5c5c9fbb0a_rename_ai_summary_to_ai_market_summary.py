"""Rename ai_summary to ai_market_summary

Revision ID: 1c5c5c9fbb0a
Revises: 1a316aea311c
Create Date: 2025-11-30 13:12:34.869718

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1c5c5c9fbb0a"
down_revision: Union[str, Sequence[str], None] = "1a316aea311c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename ai_summary to ai_market_summary in newsletters
    op.add_column("newsletters", sa.Column("ai_market_summary", sa.Text(), nullable=True))
    op.execute("UPDATE newsletters SET ai_market_summary = ai_summary")
    op.drop_column("newsletters", "ai_summary")


def downgrade() -> None:
    """Downgrade schema."""
    # Restore ai_summary from ai_market_summary
    op.add_column("newsletters", sa.Column("ai_summary", sa.TEXT(), nullable=True))
    op.execute("UPDATE newsletters SET ai_summary = ai_market_summary")
    op.drop_column("newsletters", "ai_market_summary")
