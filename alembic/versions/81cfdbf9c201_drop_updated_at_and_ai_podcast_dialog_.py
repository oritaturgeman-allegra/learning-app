"""drop_updated_at_and_ai_podcast_dialog_from_newsletters

Revision ID: 81cfdbf9c201
Revises: 3f726be61680
Create Date: 2026-01-07 21:57:14.432420

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "81cfdbf9c201"
down_revision: Union[str, Sequence[str], None] = "3f726be61680"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("newsletters") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("ai_podcast_dialog")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("newsletters") as batch_op:
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column("ai_podcast_dialog", sa.Text(), nullable=True))
