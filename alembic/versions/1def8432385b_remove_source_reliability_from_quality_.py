"""remove_source_reliability_from_quality_metrics

Revision ID: 1def8432385b
Revises: 1943c474c03d
Create Date: 2026-01-08 13:03:53.715220

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "1def8432385b"
down_revision: Union[str, Sequence[str], None] = "1943c474c03d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove source_reliability from quality_metrics JSON in existing rows."""
    # Update existing rows to remove source_reliability key from JSON
    op.execute(
        """
        UPDATE articles
        SET quality_metrics = REPLACE(quality_metrics, '"source_reliability": null, ', '')
        WHERE quality_metrics LIKE '%"source_reliability":%'
        """
    )


def downgrade() -> None:
    """Add source_reliability back to quality_metrics JSON."""
    # Add source_reliability back after content_score
    op.execute(
        """
        UPDATE articles
        SET quality_metrics = REPLACE(
            quality_metrics,
            '"content_score": null,',
            '"content_score": null, "source_reliability": null,'
        )
        WHERE quality_metrics NOT LIKE '%"source_reliability":%'
        """
    )
