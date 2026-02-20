"""replace_quality_metrics_with_confidence_score

Revision ID: b51548dd78c2
Revises: d40834a43c1c
Create Date: 2026-02-14 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b51548dd78c2"
down_revision: Union[str, Sequence[str], None] = "d40834a43c1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Replace quality_metrics (JSON Text) with confidence_score (Float)."""
    with op.batch_alter_table("articles") as batch_op:
        # Add new confidence_score column
        batch_op.add_column(
            sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0")
        )
        # Drop old quality_metrics column
        batch_op.drop_column("quality_metrics")


def downgrade() -> None:
    """Restore quality_metrics column and drop confidence_score."""
    with op.batch_alter_table("articles") as batch_op:
        # Add back quality_metrics
        batch_op.add_column(
            sa.Column(
                "quality_metrics",
                sa.Text(),
                nullable=False,
                server_default='{"freshness_score": null, "content_score": null, "relevance_score": null, "confidence": null}',
            )
        )
        # Drop confidence_score
        batch_op.drop_column("confidence_score")
