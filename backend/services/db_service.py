"""Database service for newsletter storage."""

import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.exceptions import NewsletterError
from backend.models.base import session_scope, init_db
from backend.models.newsletter import Newsletter
from backend.models.feed_provider import FeedProvider
from backend.models.article import Article
from backend.models.article_selection import ArticleSelection
from backend.models.user import User
from backend.models.podcast_generation import PodcastGeneration
from backend.models.analytics_report import AnalyticsReport
from backend.defaults import NEWS_CATEGORIES

logger = logging.getLogger(__name__)

# Retention settings (10 days - cleaned up daily via cron)
RETENTION_DAYS = 10


class DatabaseError(NewsletterError):
    """Raised when database operations fail."""

    def __init__(self, operation: str, details: str):
        self.operation = operation
        self.details = details
        super().__init__(f"Database {operation} failed: {details}")


class DatabaseService:
    """Newsletter database operations service."""

    def __init__(self) -> None:
        try:
            init_db()
        except SQLAlchemyError as e:
            raise DatabaseError("initialization", str(e))

    def save_newsletter_with_stats(
        self,
        source_stats: dict,
        sources_metadata: Optional[dict] = None,
        language: str = "en",
        sentiment: Optional[str] = None,
        podcast_dialog: Optional[str] = None,
        llm_provider: Optional[str] = None,
        tts_provider: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Newsletter:
        """Save newsletter with articles."""
        try:
            with session_scope() as session:
                newsletter = Newsletter(
                    user_id=user_id,
                    language=language,
                    podcast_dialog=podcast_dialog,
                    sentiment=sentiment,
                    llm_provider=llm_provider,
                    tts_provider=tts_provider,
                )
                session.add(newsletter)
                session.flush()

                article_metadata = sources_metadata or {}
                for category in NEWS_CATEGORIES:
                    for article_data in article_metadata.get(category, []):
                        article_ts = None
                        if ts_str := article_data.get("published_at"):
                            try:
                                article_ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            except (ValueError, AttributeError):
                                pass

                        article_kwargs = {
                            "newsletter_id": newsletter.id,
                            "category": category,
                            "source": article_data.get("source", "Unknown"),
                            "confidence_score": article_data.get("confidence_score", 0.0),
                            "ai_title": article_data.get("ai_title", ""),
                            "text": article_data.get("text"),
                            "link": article_data.get("link", ""),
                            "published_at": article_ts,
                        }
                        session.add(Article(**article_kwargs))

                session.commit()
                session.refresh(newsletter)
                session.expunge(newsletter)
                return newsletter

        except IntegrityError:
            raise DatabaseError("save_newsletter", "Data integrity violation")
        except SQLAlchemyError as e:
            raise DatabaseError("save_newsletter", str(e))

    def get_newsletter(self, newsletter_id: int) -> Optional[Newsletter]:
        """Retrieve newsletter by ID."""
        try:
            with session_scope() as session:
                newsletter = session.get(Newsletter, newsletter_id)
                if newsletter:
                    session.expunge(newsletter)
                return newsletter
        except SQLAlchemyError as e:
            raise DatabaseError("get_newsletter", str(e))

    def get_recent_newsletters(self, limit: int = 10) -> List[Newsletter]:
        """Get most recent newsletters."""
        try:
            with session_scope() as session:
                newsletters = (
                    session.query(Newsletter)
                    .order_by(Newsletter.created_at.desc())
                    .limit(limit)
                    .all()
                )
                for n in newsletters:
                    session.expunge(n)
                return newsletters
        except SQLAlchemyError as e:
            raise DatabaseError("get_recent_newsletters", str(e))

    def get_latest_newsletter(self) -> Optional[Newsletter]:
        """Get the most recent newsletter.

        Returns:
            The most recent Newsletter object, or None if no newsletters exist.
        """
        try:
            with session_scope() as session:
                newsletter = (
                    session.query(Newsletter).order_by(Newsletter.created_at.desc()).first()
                )
                if newsletter:
                    session.expunge(newsletter)
                return newsletter
        except SQLAlchemyError as e:
            raise DatabaseError("get_latest_newsletter", str(e))

    def get_latest_newsletter_with_articles(self) -> Optional[Dict[str, Any]]:
        """Get the most recent newsletter with all articles, formatted for API response.

        Returns a dict matching the /api/analyze response structure:
        {
            "newsletter": Newsletter dict,
            "sources_metadata": {
                "us": [article_dicts...],
                "israel": [article_dicts...],
                "ai": [article_dicts...],
                "crypto": [article_dicts...]
            },
            "sentiment": {"us": score, ...},
            "created_at": ISO timestamp
        }

        Returns:
            Formatted dict for API response, or None if no newsletters exist.
        """
        try:
            with session_scope() as session:
                newsletter = (
                    session.query(Newsletter).order_by(Newsletter.created_at.desc()).first()
                )
                if not newsletter:
                    return None

                # Get all articles for this newsletter
                articles = (
                    session.query(Article).filter(Article.newsletter_id == newsletter.id).all()
                )

                # Group articles by category
                sources_metadata: Dict[str, List[Dict[str, Any]]] = {
                    cat: [] for cat in NEWS_CATEGORIES
                }
                for article in articles:
                    if article.category in sources_metadata:
                        sources_metadata[article.category].append(article.to_dict())

                # Parse sentiment from newsletter
                sentiment = {}
                if newsletter.sentiment:
                    try:
                        sentiment = json.loads(newsletter.sentiment)
                    except (json.JSONDecodeError, TypeError):
                        pass

                return {
                    "newsletter": newsletter.to_dict(),
                    "sources_metadata": sources_metadata,
                    "sentiment": sentiment,
                    "llm_provider": newsletter.llm_provider,
                    "created_at": (
                        newsletter.created_at.isoformat() if newsletter.created_at else None
                    ),
                }
        except SQLAlchemyError as e:
            raise DatabaseError("get_latest_newsletter_with_articles", str(e))

    def get_sentiment_history(self, days: int = 7) -> Dict[str, Any]:
        """
        Get sentiment history for the last N days.

        Returns a dict with market keys, each containing a list of 7 daily scores.
        Most recent day is at index 6 (today), oldest at index 0.

        - Today: Returns the most recent (latest) sentiment
        - Past days: Returns the average of all sentiments from that day's scheduler runs

        Returns:
            Dict with structure: {
                "us": [score_day0, score_day1, ..., score_day6],
                "israel": [...],
                "ai": [...],
                "crypto": [...]
            }
        """
        try:
            with session_scope() as session:
                # Get date range (last N days)
                now = datetime.now(timezone.utc)
                start_date = now - timedelta(days=days - 1)
                start_of_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

                # Get newsletters from the last N days with sentiment
                newsletters = (
                    session.query(Newsletter)
                    .filter(Newsletter.created_at >= start_of_day)
                    .filter(Newsletter.sentiment.isnot(None))
                    .order_by(Newsletter.created_at.desc())
                    .all()
                )

                # Initialize result with zeros for each day
                markets = ["us", "israel", "ai", "crypto"]
                result: Dict[str, List[int]] = {market: [0] * days for market in markets}

                # Collect all sentiments per day for averaging
                # Structure: {day_index: {market: [scores]}}
                daily_scores: Dict[int, Dict[str, List[int]]] = {}
                today_date = now.date()

                for newsletter in newsletters:
                    # Calculate day index (0 = oldest, 6 = today)
                    days_ago = (today_date - newsletter.created_at.date()).days
                    if days_ago >= days:
                        continue  # Outside our range
                    day_index = days - 1 - days_ago  # Convert to 0-indexed from oldest

                    # Parse sentiment
                    try:
                        sentiment = json.loads(newsletter.sentiment)
                    except (json.JSONDecodeError, TypeError):
                        continue

                    # For today (day_index == days-1), use only the most recent (first in desc order)
                    if days_ago == 0:
                        if day_index not in daily_scores:
                            daily_scores[day_index] = {}
                            for market in markets:
                                if market in sentiment and sentiment[market] is not None:
                                    result[market][day_index] = sentiment[market]
                        # Skip remaining newsletters for today (we only want the latest)
                        continue

                    # For past days, collect all scores for averaging
                    if day_index not in daily_scores:
                        daily_scores[day_index] = {market: [] for market in markets}

                    for market in markets:
                        if market in sentiment and sentiment[market] is not None:
                            daily_scores[day_index][market].append(sentiment[market])

                # Calculate averages for past days
                for day_index, market_scores in daily_scores.items():
                    if day_index == days - 1:
                        continue  # Skip today, already handled
                    for market, scores in market_scores.items():
                        if scores:
                            result[market][day_index] = round(sum(scores) / len(scores))

                return result
        except SQLAlchemyError as e:
            raise DatabaseError("get_sentiment_history", str(e))

    def update_newsletter_podcast_dialog(self, newsletter_id: int, podcast_dialog: str) -> bool:
        """Update podcast dialog for a newsletter."""
        try:
            with session_scope() as session:
                newsletter = session.get(Newsletter, newsletter_id)
                if newsletter:
                    newsletter.podcast_dialog = podcast_dialog
                    return True
                return False
        except SQLAlchemyError as e:
            raise DatabaseError("update_newsletter_podcast_dialog", str(e))

    # ==================== User Methods ====================

    def create_user(
        self,
        email: str,
        password_hash: Optional[str] = None,
        google_id: Optional[str] = None,
        name: Optional[str] = None,
        preferred_categories: Optional[List[str]] = None,
        email_verified: bool = False,
    ) -> User:
        """Create a new user."""
        try:
            with session_scope() as session:
                user = User(
                    email=email,
                    password_hash=password_hash,
                    google_id=google_id,
                    name=name,
                    preferred_categories=(
                        json.dumps(preferred_categories)
                        if preferred_categories
                        else '["us","israel","ai","crypto"]'
                    ),
                    email_verified=email_verified,
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                session.expunge(user)
                return user
        except IntegrityError:
            raise DatabaseError("create_user", "User with this email or Google ID already exists")
        except SQLAlchemyError as e:
            raise DatabaseError("create_user", str(e))

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            with session_scope() as session:
                user = session.get(User, user_id)
                if user:
                    session.expunge(user)
                return user
        except SQLAlchemyError as e:
            raise DatabaseError("get_user_by_id", str(e))

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            with session_scope() as session:
                user = session.query(User).filter(User.email == email).first()
                if user:
                    session.expunge(user)
                return user
        except SQLAlchemyError as e:
            raise DatabaseError("get_user_by_email", str(e))

    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google OAuth ID."""
        try:
            with session_scope() as session:
                user = session.query(User).filter(User.google_id == google_id).first()
                if user:
                    session.expunge(user)
                return user
        except SQLAlchemyError as e:
            raise DatabaseError("get_user_by_google_id", str(e))

    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        preferred_categories: Optional[List[str]] = None,
        email_notifications: Optional[bool] = None,
    ) -> Optional[User]:
        """Update user profile."""
        try:
            with session_scope() as session:
                user = session.get(User, user_id)
                if not user:
                    return None
                if name is not None:
                    user.name = name
                if preferred_categories is not None:
                    user.preferred_categories = json.dumps(preferred_categories)
                if email_notifications is not None:
                    user.email_notifications = email_notifications
                session.commit()
                session.refresh(user)
                session.expunge(user)
                return user
        except SQLAlchemyError as e:
            raise DatabaseError("update_user", str(e))

    def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            with session_scope() as session:
                user = session.get(User, user_id)
                if user:
                    user.last_login_at = datetime.now()
                    return True
                return False
        except SQLAlchemyError as e:
            raise DatabaseError("update_user_last_login", str(e))

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        try:
            with session_scope() as session:
                user = session.get(User, user_id)
                if user:
                    user.is_active = False
                    return True
                return False
        except SQLAlchemyError as e:
            raise DatabaseError("deactivate_user", str(e))

    # ==================== Email Verification ====================

    def get_user_by_verification_token(self, token: str) -> Optional[User]:
        """Get user by verification token."""
        try:
            with session_scope() as session:
                user = session.query(User).filter(User.verification_token == token).first()
                if user:
                    session.expunge(user)
                return user
        except SQLAlchemyError as e:
            raise DatabaseError("get_user_by_verification_token", str(e))

    def set_verification_token(self, user_id: int, token: str, expires_at: datetime) -> bool:
        """Set verification token for a user."""
        try:
            with session_scope() as session:
                user = session.get(User, user_id)
                if user:
                    user.verification_token = token
                    user.verification_token_expires_at = expires_at
                    return True
                return False
        except SQLAlchemyError as e:
            raise DatabaseError("set_verification_token", str(e))

    def clear_verification_token(self, user_id: int) -> bool:
        """Clear verification token after successful verification."""
        try:
            with session_scope() as session:
                user = session.get(User, user_id)
                if user:
                    user.verification_token = None
                    user.verification_token_expires_at = None
                    return True
                return False
        except SQLAlchemyError as e:
            raise DatabaseError("clear_verification_token", str(e))

    def mark_email_verified(self, user_id: int) -> Optional[User]:
        """Mark user's email as verified and clear token."""
        try:
            with session_scope() as session:
                user = session.get(User, user_id)
                if user:
                    user.email_verified = True
                    user.verification_token = None
                    user.verification_token_expires_at = None
                    session.commit()
                    session.refresh(user)
                    session.expunge(user)
                    return user
                return None
        except SQLAlchemyError as e:
            raise DatabaseError("mark_email_verified", str(e))

    def get_user_newsletters(self, user_id: int, limit: int = 10) -> List[Newsletter]:
        """Get newsletters created by a specific user."""
        try:
            with session_scope() as session:
                newsletters = (
                    session.query(Newsletter)
                    .filter(Newsletter.user_id == user_id)
                    .order_by(Newsletter.created_at.desc())
                    .limit(limit)
                    .all()
                )
                for n in newsletters:
                    session.expunge(n)
                return newsletters
        except SQLAlchemyError as e:
            raise DatabaseError("get_user_newsletters", str(e))

    # ==================== Podcast Generation Tracking ====================

    def get_user_podcast_generation_count(self, user_id: int, date: datetime) -> int:
        """Count podcast generations for a user on a given UTC date.

        Only counts actual generations (cache misses), not cache hits.

        Args:
            user_id: The user ID to check
            date: The date to check (uses date part only, UTC)

        Returns:
            Number of podcast generations on that date
        """
        try:
            with session_scope() as session:
                start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)

                count = (
                    session.query(PodcastGeneration)
                    .filter(
                        PodcastGeneration.user_id == user_id,
                        PodcastGeneration.cached == False,  # noqa: E712 - SQLAlchemy requires ==
                        PodcastGeneration.created_at >= start_of_day,
                        PodcastGeneration.created_at < end_of_day,
                    )
                    .count()
                )
                return count
        except SQLAlchemyError as e:
            raise DatabaseError("get_user_podcast_generation_count", str(e))

    def record_podcast_generation(
        self, user_id: int, categories: List[str], cache_key: str, cached: bool = False
    ) -> PodcastGeneration:
        """Record a podcast request event.

        Called for both cache hits and misses to track all usage.
        Only cache misses (cached=False) count against the daily limit.

        Args:
            user_id: The user who triggered the request
            categories: List of categories used
            cache_key: The audio cache key
            cached: True if served from cache, False if newly generated

        Returns:
            The created PodcastGeneration record
        """
        try:
            with session_scope() as session:
                record = PodcastGeneration(
                    user_id=user_id,
                    categories=json.dumps(sorted(categories)),
                    cache_key=cache_key,
                    cached=cached,
                )
                session.add(record)
                session.commit()
                session.refresh(record)
                session.expunge(record)
                return record
        except SQLAlchemyError as e:
            raise DatabaseError("record_podcast_generation", str(e))

    # ==================== Feed Provider Stats ====================

    def update_feed_providers(self, source_stats: dict) -> None:
        """Update accumulated feed provider stats."""
        try:
            now = datetime.now(timezone.utc)
            with session_scope() as session:
                for category in NEWS_CATEGORIES:
                    for stat in source_stats.get(category, []):
                        source_name = stat.get("name", "Unknown")
                        feed_url = stat.get("url", "")
                        is_active = stat.get("status") == "active"

                        # Try to find existing provider
                        provider = (
                            session.query(FeedProvider)
                            .filter(
                                FeedProvider.source_name == source_name,
                                FeedProvider.category == category,
                            )
                            .first()
                        )

                        if provider:
                            # Update existing
                            provider.total_runs += 1
                            if is_active:
                                provider.success_count += 1
                            provider.reliability = round(
                                (
                                    provider.success_count / provider.total_runs
                                    if provider.total_runs > 0
                                    else 0.0
                                ),
                                2,
                            )
                            provider.last_updated = now
                            # Update URL if changed
                            if feed_url and provider.feed_url != feed_url:
                                provider.feed_url = feed_url
                        else:
                            # Create new
                            session.add(
                                FeedProvider(
                                    source_name=source_name,
                                    feed_url=feed_url,
                                    category=category,
                                    total_runs=1,
                                    success_count=1 if is_active else 0,
                                    reliability=1.0 if is_active else 0.0,
                                    last_updated=now,
                                )
                            )
                session.commit()
                logger.info("Updated feed provider stats")
        except SQLAlchemyError as e:
            logger.error(f"Error updating feed providers: {e}")

    def get_all_feeds(self) -> List[Tuple[str, str, str]]:
        """Get all feed providers with URLs from database.

        Returns:
            List of tuples: (feed_url, source_name, category)
        """
        try:
            with session_scope() as session:
                providers = (
                    session.query(FeedProvider)
                    .filter(FeedProvider.feed_url.isnot(None))
                    .filter(FeedProvider.feed_url != "")
                    .all()
                )
                return [(p.feed_url, p.source_name, p.category) for p in providers]
        except SQLAlchemyError as e:
            logger.error(f"Error getting feeds from DB: {e}")
            return []

    # ==================== Article Selection Analytics ====================

    def save_article_selections(
        self,
        selections: List[Dict[str, Any]],
        newsletter_id: Optional[int] = None,
    ) -> int:
        """
        Save article selection records for analytics.

        Args:
            selections: List of dicts with keys:
                - source_name: str
                - category: str
                - title: str
                - link: str
                - selected: bool
            newsletter_id: Optional newsletter ID for selected articles

        Returns:
            Number of records saved
        """
        if not selections:
            return 0

        try:
            now = datetime.now(timezone.utc)
            with session_scope() as session:
                for sel in selections:
                    record = ArticleSelection(
                        source_name=sel.get("source_name", "Unknown"),
                        category=sel.get("category", "unknown"),
                        title=sel.get("title", "")[:500],  # Truncate to 500 chars
                        link=sel.get("link", ""),
                        selected=sel.get("selected", False),
                        newsletter_id=newsletter_id if sel.get("selected") else None,
                        fetched_at=now,
                    )
                    session.add(record)
                session.commit()
                logger.info(f"Saved {len(selections)} article selections")
                return len(selections)
        except SQLAlchemyError as e:
            logger.error(f"Error saving article selections: {e}")
            return 0

    def get_article_selections_for_date(
        self,
        target_date: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Get all article selections for a specific date.

        Args:
            target_date: The date to query (uses date part only)

        Returns:
            List of selection records as dicts
        """
        try:
            # Get start and end of the target day in UTC
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            with session_scope() as session:
                selections = (
                    session.query(ArticleSelection)
                    .filter(ArticleSelection.fetched_at >= start_of_day)
                    .filter(ArticleSelection.fetched_at < end_of_day)
                    .order_by(ArticleSelection.category, ArticleSelection.source_name)
                    .all()
                )
                return [sel.to_dict() for sel in selections]
        except SQLAlchemyError as e:
            logger.error(f"Error getting article selections: {e}")
            return []

    def get_feed_provider_stats(self) -> List[Dict[str, Any]]:
        """
        Get all feed provider statistics.

        Returns:
            List of feed provider records as dicts
        """
        try:
            with session_scope() as session:
                providers = (
                    session.query(FeedProvider)
                    .order_by(FeedProvider.category, FeedProvider.reliability.desc())
                    .all()
                )
                return [p.to_dict() for p in providers]
        except SQLAlchemyError as e:
            logger.error(f"Error getting feed provider stats: {e}")
            return []

    def get_selection_summary_for_date(
        self,
        target_date: datetime,
    ) -> Dict[str, Any]:
        """
        Get aggregated selection statistics for a specific date.

        Args:
            target_date: The date to query

        Returns:
            Dict with aggregated stats by source and category
        """
        try:
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            with session_scope() as session:
                selections = (
                    session.query(ArticleSelection)
                    .filter(ArticleSelection.fetched_at >= start_of_day)
                    .filter(ArticleSelection.fetched_at < end_of_day)
                    .all()
                )

                # Aggregate by source and category
                by_source: Dict[str, Dict[str, Any]] = {}
                by_category: Dict[str, Dict[str, Any]] = {}

                for sel in selections:
                    key = f"{sel.source_name}|{sel.category}"
                    if key not in by_source:
                        by_source[key] = {
                            "source_name": sel.source_name,
                            "category": sel.category,
                            "total": 0,
                            "selected": 0,
                            "rejected_titles": [],
                        }
                    by_source[key]["total"] += 1
                    if sel.selected:
                        by_source[key]["selected"] += 1
                    else:
                        # Keep up to 5 rejected titles for context
                        if len(by_source[key]["rejected_titles"]) < 5:
                            by_source[key]["rejected_titles"].append(sel.title[:100])

                    # Category totals
                    if sel.category not in by_category:
                        by_category[sel.category] = {"total": 0, "selected": 0}
                    by_category[sel.category]["total"] += 1
                    if sel.selected:
                        by_category[sel.category]["selected"] += 1

                # Calculate acceptance rates
                for stats in by_source.values():
                    stats["acceptance_rate"] = round(
                        stats["selected"] / stats["total"] if stats["total"] > 0 else 0,
                        2,
                    )

                for stats in by_category.values():
                    stats["acceptance_rate"] = round(
                        stats["selected"] / stats["total"] if stats["total"] > 0 else 0,
                        2,
                    )

                return {
                    "date": target_date.date().isoformat(),
                    "total_articles": len(selections),
                    "total_selected": sum(1 for s in selections if s.selected),
                    "by_source": list(by_source.values()),
                    "by_category": by_category,
                }
        except SQLAlchemyError as e:
            logger.error(f"Error getting selection summary: {e}")
            return {
                "date": target_date.date().isoformat(),
                "total_articles": 0,
                "total_selected": 0,
                "by_source": [],
                "by_category": {},
            }

    # ==================== Retention Cleanup ====================

    def save_analytics_report(self, report_date: str, report_data: str) -> None:
        """Save an analytics report, replacing any existing report for the same date."""
        try:
            with session_scope() as session:
                existing = (
                    session.query(AnalyticsReport)
                    .filter(AnalyticsReport.report_date == report_date)
                    .first()
                )
                if existing:
                    existing.report_data = report_data
                    existing.created_at = datetime.now(timezone.utc)
                else:
                    report = AnalyticsReport(
                        report_date=report_date,
                        report_data=report_data,
                    )
                    session.add(report)
        except SQLAlchemyError as e:
            raise DatabaseError("save_analytics_report", str(e))

    def get_latest_analytics_report(self) -> Optional[Dict[str, Any]]:
        """Get the most recent analytics report as a parsed dict."""
        try:
            with session_scope() as session:
                report = (
                    session.query(AnalyticsReport)
                    .order_by(AnalyticsReport.created_at.desc())
                    .first()
                )
                if report:
                    return json.loads(report.report_data)
                return None
        except SQLAlchemyError as e:
            logger.error(f"Failed to get latest analytics report: {e}")
            return None

    def run_retention_cleanup(self) -> Dict[str, int]:
        """
        Delete old data based on retention policy (10 days).
        Returns count of deleted rows per table.
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=RETENTION_DAYS)
        deleted = {"articles": 0, "newsletters": 0, "article_selections": 0}

        try:
            with session_scope() as session:
                # Delete old articles
                result = (
                    session.query(Article)
                    .filter(Article.fetched_at < cutoff)
                    .delete(synchronize_session=False)
                )
                deleted["articles"] = result

                # Delete old newsletters
                result = (
                    session.query(Newsletter)
                    .filter(Newsletter.created_at < cutoff)
                    .delete(synchronize_session=False)
                )
                deleted["newsletters"] = result

                # Delete old article selections
                result = (
                    session.query(ArticleSelection)
                    .filter(ArticleSelection.fetched_at < cutoff)
                    .delete(synchronize_session=False)
                )
                deleted["article_selections"] = result

                session.commit()

            total = sum(deleted.values())
            if total > 0:
                logger.info(f"Retention cleanup ({RETENTION_DAYS} days): deleted {deleted}")
            return deleted

        except SQLAlchemyError as e:
            logger.error(f"Error during retention cleanup: {e}")
            return deleted


_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get global database service singleton."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
