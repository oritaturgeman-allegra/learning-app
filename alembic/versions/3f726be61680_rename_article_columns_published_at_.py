"""rename_article_columns_published_at_fetched_at

Revision ID: 3f726be61680
Revises: 2cfde494476b
Create Date: 2026-01-07 21:52:22.075761

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3f726be61680"
down_revision: Union[str, Sequence[str], None] = "2cfde494476b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename columns in articles table
    with op.batch_alter_table("articles") as batch_op:
        batch_op.alter_column("article_timestamp", new_column_name="published_at")
        batch_op.alter_column("created_at", new_column_name="fetched_at")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("articles") as batch_op:
        batch_op.alter_column("published_at", new_column_name="article_timestamp")
        batch_op.alter_column("fetched_at", new_column_name="created_at")
