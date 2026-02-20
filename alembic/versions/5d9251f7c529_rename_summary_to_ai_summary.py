"""Rename summary to ai_summary

Revision ID: 5d9251f7c529
Revises: 877eb8ba9044
Create Date: 2025-11-30 12:32:12.211793

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d9251f7c529"
down_revision: Union[str, Sequence[str], None] = "877eb8ba9044"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new column
    op.add_column("newsletters", sa.Column("ai_summary", sa.Text(), nullable=True))
    # Copy data from old column to new column
    op.execute("UPDATE newsletters SET ai_summary = summary")
    # Drop old column
    op.drop_column("newsletters", "summary")


def downgrade() -> None:
    """Downgrade schema."""
    # Add old column back
    op.add_column("newsletters", sa.Column("summary", sa.TEXT(), nullable=True))
    # Copy data back
    op.execute("UPDATE newsletters SET summary = ai_summary")
    # Drop new column
    op.drop_column("newsletters", "ai_summary")
