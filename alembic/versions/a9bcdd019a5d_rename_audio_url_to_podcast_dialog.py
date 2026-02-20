"""rename audio_url to podcast_dialog

Revision ID: a9bcdd019a5d
Revises: 76c10cf3a634
Create Date: 2026-01-29 20:19:50.957504

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a9bcdd019a5d"
down_revision: Union[str, Sequence[str], None] = "76c10cf3a634"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename audio_url column to podcast_dialog in newsletters table."""
    with op.batch_alter_table("newsletters", schema=None) as batch_op:
        batch_op.alter_column("audio_url", new_column_name="podcast_dialog", type_=sa.Text())


def downgrade() -> None:
    """Rename podcast_dialog column back to audio_url."""
    with op.batch_alter_table("newsletters", schema=None) as batch_op:
        batch_op.alter_column("podcast_dialog", new_column_name="audio_url", type_=sa.String(500))
