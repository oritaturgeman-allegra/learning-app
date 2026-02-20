"""
AnalyticsReport model for persisting daily feed analytics reports.

Stores the full JSON report so the copy-to-clipboard page works
across server restarts and ephemeral filesystems (e.g., Railway).
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class AnalyticsReport(Base):
    """
    Stores analytics report JSON for the copy-to-clipboard page.

    Only the latest report per date is kept (upserted by report_date).

    Attributes:
        id: Primary key
        report_date: The date the report covers (e.g., "2026-02-17")
        report_data: Full JSON report as text
        created_at: When the report was generated
    """

    __tablename__ = "analytics_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    report_data: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<AnalyticsReport(id={self.id}, date='{self.report_date}')>"
