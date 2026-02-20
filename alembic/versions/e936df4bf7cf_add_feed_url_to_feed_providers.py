"""add_feed_url_to_feed_providers

Revision ID: e936df4bf7cf
Revises: 036b4b57524f
Create Date: 2026-01-10 15:48:44.965152

Adds feed_url column to store RSS feed URLs in database.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e936df4bf7cf"
down_revision: Union[str, Sequence[str], None] = "036b4b57524f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Feed URL mappings (source_name -> url)
FEED_URLS = {
    # US feeds
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Nasdaq Stocks": "https://www.nasdaq.com/feed/rssoutbound?category=stocks",
    "Nasdaq Articles": "https://www.nasdaq.com/feed/rssoutbound?category=articles",
    "CNBC": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "Investing.com News": "https://www.investing.com/rss/news.rss",
    "Nasdaq Earnings": "https://www.nasdaq.com/feed/rssoutbound?category=Earnings",
    "Investing.com Commodities": "https://www.investing.com/rss/news_285.rss",
    "FT": "https://www.ft.com/markets?format=rss",
    # Israel feeds
    "Globes": "https://www.globes.co.il/webservice/rss/rssfeeder.asmx/FeederNode?iID=585",
    "TheMarker": "https://www.themarker.com/srv/tm-markets",
    # AI feeds
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat": "https://venturebeat.com/category/ai/feed/",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    # Crypto feeds
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/feed",
    "CryptoPotato": "https://cryptopotato.com/feed/",
    "Decrypt": "https://decrypt.co/feed",
}


def upgrade() -> None:
    """Add feed_url column and populate with existing URLs."""
    # Add the column
    op.add_column("feed_providers", sa.Column("feed_url", sa.String(500), nullable=True))

    # Populate feed_url for existing providers
    for source_name, url in FEED_URLS.items():
        escaped_url = url.replace("'", "''")
        escaped_name = source_name.replace("'", "''")
        op.execute(
            f"UPDATE feed_providers SET feed_url = '{escaped_url}' "
            f"WHERE source_name = '{escaped_name}'"
        )


def downgrade() -> None:
    """Remove feed_url column."""
    op.drop_column("feed_providers", "feed_url")
