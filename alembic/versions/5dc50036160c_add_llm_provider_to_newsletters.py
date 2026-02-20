"""add_llm_provider_to_newsletters

Revision ID: 5dc50036160c
Revises: a660e15c1b8b
Create Date: 2025-12-10 16:27:12.032862

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5dc50036160c"
down_revision: Union[str, Sequence[str], None] = "a660e15c1b8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("newsletters", sa.Column("llm_provider", sa.String(50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("newsletters", "llm_provider")
