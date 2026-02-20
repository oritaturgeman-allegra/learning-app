"""drop_ai_title_en_and_clean_old_articles

Revision ID: 2cfde494476b
Revises: 161ecb4ddd29
Create Date: 2026-01-07 21:38:28.144643

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2cfde494476b"
down_revision: Union[str, Sequence[str], None] = "161ecb4ddd29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Delete articles older than 7 days
    op.execute("DELETE FROM articles WHERE created_at < datetime('now', '-7 days')")

    # Drop ai_title_en column using batch operation (required for SQLite)
    with op.batch_alter_table("articles") as batch_op:
        batch_op.drop_column("ai_title_en")


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add ai_title_en column
    with op.batch_alter_table("articles") as batch_op:
        batch_op.add_column(sa.Column("ai_title_en", sa.Text(), nullable=True))
