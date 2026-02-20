"""add_tts_provider_to_newsletters

Revision ID: 2bbcede10542
Revises: 5dc50036160c
Create Date: 2025-12-10 17:03:42.872313

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2bbcede10542"
down_revision: Union[str, Sequence[str], None] = "5dc50036160c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("newsletters", sa.Column("tts_provider", sa.String(50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("newsletters", "tts_provider")
