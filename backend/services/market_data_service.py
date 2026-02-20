"""Market Data Service - fetches RSS feeds for market news."""

import asyncio
import calendar
import feedparser
import html
import logging
import re
import ssl
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type, AsyncRetrying
import aiohttp

from backend.config import config
from backend.defaults import NEWS_CATEGORIES, RSS_FETCH_HEADERS
from backend.exceptions import FeedFetchError
from backend.services.db_service import get_db_service
from backend.services.quality_metrics_service import (
    select_top_articles_with_metadata,
)

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """News article from RSS feed."""

    text: str
    source: str
    published_at: str  # ISO format timestamp
    original_title: str  # RSS title - ai_title is generated later by LLM
    link: str
    freshness_score: float  # Calculated from published_at (used for pre-filtering, not stored)
    confidence_score: float = 0.0  # LLM-assigned quality score (0.0-1.0), stored in DB


@dataclass
class SourceStats:
    """RSS source health stats."""

    name: str
    count: int
    status: str
    url: str = ""


def _clean_html(text: str) -> str:
    """Remove HTML tags and decode HTML entities from text."""
    text = re.sub("<[^<]+?>", "", text)
    return html.unescape(text)


def _extract_published_date(entry: Any) -> Optional[datetime]:
    """Extract published date from RSS entry.

    Note: feedparser always returns parsed dates in UTC, so we use
    calendar.timegm() (not time.mktime()) to correctly convert to timestamp.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        timestamp = calendar.timegm(entry.published_parsed)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        timestamp = calendar.timegm(entry.updated_parsed)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return None


def _calc_freshness_score(published_date: datetime) -> float:
    """Calculate freshness score based on article age.

    Returns:
        1.0 for very fresh (≤2h), decays to 0.1 for old (≥12h)
    """
    now = datetime.now(tz=timezone.utc)
    age_hours = (now - published_date).total_seconds() / 3600

    if age_hours <= 2:
        return 1.0
    elif age_hours >= 12:
        return 0.1
    else:
        # Linear decay from 1.0 to 0.1 between 2h and 12h
        return round(1.0 - (age_hours - 2) * 0.09, 2)  # 0.9 / 10 hours = 0.09 per hour


def _parse_feed_entries(feed: Any, source_name: str, max_items: int) -> List[Article]:
    """Parse RSS feed entries into Article objects."""
    articles: List[Article] = []
    cutoff_time = datetime.now(tz=timezone.utc) - timedelta(hours=config.intraday_hours)

    for entry in feed.entries:
        published_date = _extract_published_date(entry)
        if published_date and published_date < cutoff_time:
            continue
        if not published_date:
            published_date = datetime.now(tz=timezone.utc)

        title = html.unescape(entry.get("title", "").strip())
        summary = entry.get("summary", entry.get("description", "")).strip()
        link = entry.get("link", "").strip()

        if summary and summary != title:
            article_text = f"{title}: {_clean_html(summary)[:200]}"
        else:
            article_text = title

        if article_text:
            articles.append(
                Article(
                    text=article_text,
                    source=source_name,
                    published_at=published_date.isoformat(),
                    original_title=title,
                    link=link,
                    freshness_score=_calc_freshness_score(published_date),
                )
            )

        if len(articles) >= max_items:
            break

    return articles


async def fetch_market_data_async(categories: Optional[List[str]] = None) -> Dict[str, Any]:
    """Fetch market news from RSS sources in parallel.

    Args:
        categories: List of categories to fetch. If None, fetches all categories.
    """
    if categories is None:
        categories = NEWS_CATEGORIES.copy()

    logger.info(
        f"Fetching market news (last {config.intraday_hours} hours, categories={categories})..."
    )

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    articles_by_category: Dict[str, List[Article]] = {cat: [] for cat in NEWS_CATEGORIES}
    stats_by_category: Dict[str, List[SourceStats]] = {cat: [] for cat in NEWS_CATEGORIES}

    async def fetch_feed(url: str, name: str, category: str) -> Tuple[str, str, List[Article]]:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        ):
            with attempt:
                try:
                    async with session.get(
                        url,
                        headers=RSS_FETCH_HEADERS,
                        timeout=aiohttp.ClientTimeout(total=config.feed_timeout),
                        ssl=False,
                    ) as response:
                        response.raise_for_status()
                        content = await response.read()

                    feed = feedparser.parse(content)
                    feed_articles = _parse_feed_entries(feed, name, max_items=5)
                    return (category, name, feed_articles)

                except aiohttp.ClientResponseError as e:
                    raise FeedFetchError(url, f"HTTP {e.status}")
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    raise

        return (category, name, [])

    # Get feeds from database, filter by selected categories
    all_feeds = get_db_service().get_all_feeds()
    filtered_feeds = [(url, name, cat) for url, name, cat in all_feeds if cat in categories]

    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_feed(url, name, cat) for url, name, cat in filtered_feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        url, name, category = filtered_feeds[i]
        if isinstance(result, BaseException):
            stats_by_category[category].append(
                SourceStats(name=name, count=0, status="inactive", url=url)
            )
        else:
            cat, source_name, feed_articles = result
            count = len(feed_articles)
            stats_by_category[cat].append(
                SourceStats(
                    name=source_name,
                    count=count,
                    status="active" if count > 0 else "inactive",
                    url=url,
                )
            )
            articles_by_category[cat].extend(feed_articles)

    # Log warning for empty categories but don't fail
    for cat in categories:
        if not articles_by_category[cat]:
            logger.warning(
                f"No articles found for category '{cat}' in last {config.intraday_hours} hours"
            )

    # Step 1: Pre-filter to limit LLM input size (freshness is only available metric here)
    # The LLM will then rank by: relevance → content quality → freshness → dedup
    MAX_FOR_LLM = 15  # Max articles per category to send to LLM for ranking
    for cat in NEWS_CATEGORIES:
        articles = articles_by_category[cat]
        if len(articles) > MAX_FOR_LLM:
            # Keep top N freshest - LLM will re-rank by quality/relevance
            articles.sort(key=lambda a: a.freshness_score, reverse=True)
            articles_by_category[cat] = articles[:MAX_FOR_LLM]
            logger.info(f"Pre-filtered {cat}: {len(articles)} -> {MAX_FOR_LLM} for LLM")

    # Step 2: LLM direct selection (replaces scoring + dedup in ONE call per category)
    # LLM applies: relevance filter -> content quality ranking -> freshness tiebreaker -> dedup
    top_articles = {}
    all_selection_records = []
    for cat in NEWS_CATEGORIES:
        selection_result = select_top_articles_with_metadata(
            articles_by_category[cat],
            category=cat,
            max_count=config.max_articles_per_category,
        )
        top_articles[cat] = selection_result.selected_articles
        all_selection_records.extend(selection_result.selection_records)

    # Build article metadata dict
    def article_to_dict(article: Article) -> dict:
        data = vars(article).copy()
        # Remove legacy fields that are no longer stored in DB
        data.pop("freshness_score", None)
        data.pop("content_quality", None)
        data.pop("relevance_score", None)
        # confidence_score is already in the dict from the Article dataclass
        return data

    return {
        "raw_us_market_news": [f"[{i}] {a.text}" for i, a in enumerate(top_articles["us"])],
        "raw_israel_market_news": [f"[{i}] {a.text}" for i, a in enumerate(top_articles["israel"])],
        "raw_ai_news": [f"[{i}] {a.text}" for i, a in enumerate(top_articles["ai"])],
        "raw_crypto_news": [f"[{i}] {a.text}" for i, a in enumerate(top_articles["crypto"])],
        "articles_metadata": {
            cat: [article_to_dict(a) for a in top_articles[cat]] for cat in NEWS_CATEGORIES
        },
        "source_stats": {cat: [vars(s) for s in stats_by_category[cat]] for cat in NEWS_CATEGORIES},
        "selection_records": all_selection_records,
    }
