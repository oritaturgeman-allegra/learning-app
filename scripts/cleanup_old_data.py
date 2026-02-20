#!/usr/bin/env python3
"""
Daily cleanup script for newsletter database.
Removes newsletters and articles older than 10 days.

Run via cron at 8:00 AM US Eastern:
    0 8 * * * cd /Users/oritturgeman/Projects/capital_market_newsletter && .venv/bin/python scripts/cleanup_old_data.py

Note: Adjust cron time based on your Mac's timezone.
If Mac is in Israel (UTC+2), 8am US Eastern (UTC-5) = 3pm Israel time.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.db_service import get_db_service  # noqa: E402


def main():
    """Run retention cleanup."""
    print("Starting retention cleanup...")
    db_service = get_db_service()
    result = db_service.run_retention_cleanup()

    total = result["articles"] + result["newsletters"]
    if total > 0:
        print(
            f"Cleanup complete: {result['articles']} articles, {result['newsletters']} newsletters deleted"
        )
    else:
        print("Cleanup complete: no old data to delete")

    return 0


if __name__ == "__main__":
    sys.exit(main())
