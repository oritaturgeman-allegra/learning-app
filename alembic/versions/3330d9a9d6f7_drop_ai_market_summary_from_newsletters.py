"""drop_ai_market_summary_from_newsletters

Revision ID: 3330d9a9d6f7
Revises: 4361ddeb78b7
Create Date: 2026-01-07 22:26:43.585877

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3330d9a9d6f7"
down_revision: Union[str, Sequence[str], None] = "4361ddeb78b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("newsletters") as batch_op:
        batch_op.drop_column("ai_market_summary")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("newsletters") as batch_op:
        batch_op.add_column(sa.Column("ai_market_summary", sa.Text(), nullable=True))
