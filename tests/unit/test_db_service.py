"""
Unit tests for database service.

Note: conftest.py sets DATABASE_URL to a temp file before any imports,
ensuring all tests use an isolated test database.
"""

from datetime import datetime, timezone

import pytest

from backend.models.base import Base, get_engine, session_scope
from backend.models.newsletter import Newsletter
from backend.models.feed_provider import FeedProvider
from backend.models.article import Article
from backend.models.user import User
from backend.services.db_service import DatabaseService, DatabaseError


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create fresh tables for each test."""
    engine = get_engine()
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up data after each test
    with session_scope() as session:
        session.query(Article).delete()
        session.query(FeedProvider).delete()
        session.query(Newsletter).delete()
        session.query(User).delete()


class TestNewsletter:
    """Tests for Newsletter model."""

    def test_newsletter_creation(self):
        """Test creating a newsletter."""
        with session_scope() as session:
            newsletter = Newsletter(
                language="en",
            )
            session.add(newsletter)
            session.commit()
            assert newsletter.id is not None
            assert newsletter.language == "en"

    def test_newsletter_defaults(self):
        """Test newsletter default values."""
        with session_scope() as session:
            newsletter = Newsletter()
            session.add(newsletter)
            session.commit()
            assert newsletter.language == "en"
            assert newsletter.created_at is not None

    def test_newsletter_to_dict(self):
        """Test newsletter to_dict method."""
        newsletter = Newsletter(
            id=1,
            language="en",
            sentiment='{"us": 65, "israel": 48}',
            llm_provider="openai",
            tts_provider="gemini",
        )
        result = newsletter.to_dict()
        assert result["id"] == 1
        assert result["language"] == "en"
        assert result["sentiment"] == {"us": 65, "israel": 48}
        assert result["llm_provider"] == "openai"
        assert result["tts_provider"] == "gemini"


class TestArticle:
    """Tests for Article model."""

    def test_article_creation(self):
        """Test creating an article."""
        with session_scope() as session:
            newsletter = Newsletter()
            session.add(newsletter)
            session.flush()

            article = Article(
                newsletter_id=newsletter.id,
                category="israel",
                source="Globes",
                ai_title="Test Hebrew Article",
                text="Article description text",
                link="https://globes.co.il/article/123",
            )
            session.add(article)
            session.commit()
            assert article.id is not None
            assert article.source == "Globes"

    def test_article_to_dict(self):
        """Test article to_dict method."""
        article = Article(
            id=1,
            newsletter_id=10,
            category="us",
            source="CNBC",
            ai_title="Market Update",
            text="Markets are up today",
            link="https://cnbc.com/article",
        )
        result = article.to_dict()
        assert result["id"] == 1
        assert result["category"] == "us"
        assert result["source"] == "CNBC"
        assert result["ai_title"] == "Market Update"
        assert result["link"] == "https://cnbc.com/article"


class TestDatabaseService:
    """Tests for DatabaseService."""

    def test_save_newsletter_with_stats(self):
        """Test saving newsletter with source stats."""
        service = DatabaseService()
        source_stats = {
            "us": [
                {"name": "Yahoo Finance", "status": "active", "count": 5},
                {"name": "CNBC", "status": "inactive", "count": 0},
            ],
            "israel": [],
            "ai": [],
        }

        newsletter = service.save_newsletter_with_stats(
            source_stats=source_stats,
            language="en",
        )

        assert newsletter.id is not None
        assert newsletter.language == "en"

    def test_save_newsletter_with_articles(self):
        """Test saving newsletter with articles from sources_metadata."""
        service = DatabaseService()
        sources_metadata = {
            "us": [
                {
                    "link": "https://example.com/article1",
                    "source": "CNBC",
                    "text": "Article text here",
                    "published_at": "2025-11-30T10:00:00",
                    "ai_title": "Test Article Title",
                }
            ],
            "israel": [
                {
                    "link": "https://globes.co.il/news/123",
                    "source": "Globes",
                    "text": "Hebrew article text",
                    "published_at": "2025-11-30T07:50:00",
                    "ai_title": "Hebrew Article Title",
                }
            ],
            "ai": [],
        }
        source_stats = {"us": [], "israel": [], "ai": []}

        newsletter = service.save_newsletter_with_stats(
            source_stats=source_stats,
            sources_metadata=sources_metadata,
        )

        # Verify articles were saved
        with session_scope() as session:
            saved_articles = session.query(Article).filter_by(newsletter_id=newsletter.id).all()
            assert len(saved_articles) == 2
            sources = [a.source for a in saved_articles]
            assert "CNBC" in sources
            assert "Globes" in sources

    def test_save_newsletter_with_sentiment(self):
        """Test saving newsletter with sentiment."""
        service = DatabaseService()
        newsletter = service.save_newsletter_with_stats(
            source_stats={"us": [], "israel": [], "ai": []},
            sentiment="bullish",
        )
        assert newsletter.sentiment == "bullish"

    def test_save_newsletter_with_llm_provider(self):
        """Test saving newsletter with llm_provider."""
        service = DatabaseService()
        newsletter = service.save_newsletter_with_stats(
            source_stats={"us": [], "israel": [], "ai": []},
            llm_provider="gemini",
        )
        assert newsletter.llm_provider == "gemini"

    def test_save_newsletter_with_tts_provider(self):
        """Test saving newsletter with tts_provider."""
        service = DatabaseService()
        newsletter = service.save_newsletter_with_stats(
            source_stats={"us": [], "israel": [], "ai": []},
            tts_provider="openai",
        )
        assert newsletter.tts_provider == "openai"

    def test_get_recent_newsletters(self):
        """Test getting recent newsletters."""
        service = DatabaseService()

        # Save multiple newsletters
        for i in range(5):
            service.save_newsletter_with_stats(
                source_stats={"us": [], "israel": [], "ai": []},
            )

        recent = service.get_recent_newsletters(limit=3)
        assert len(recent) == 3

    def test_get_sentiment_history(self):
        """Test getting sentiment history."""
        import json

        service = DatabaseService()

        # Save newsletter with sentiment
        service.save_newsletter_with_stats(
            source_stats={"us": [], "israel": [], "ai": []},
            sentiment=json.dumps({"us": 65, "israel": 48, "crypto": 72}),
        )

        history = service.get_sentiment_history(days=7)

        # Should have all 4 markets
        assert "us" in history
        assert "israel" in history
        assert "ai" in history
        assert "crypto" in history

        # Each market should have 7 days
        assert len(history["us"]) == 7
        assert len(history["israel"]) == 7

        # Today's value (index 6) should have our sentiment
        assert history["us"][6] == 65
        assert history["israel"][6] == 48
        assert history["crypto"][6] == 72
        assert history["ai"][6] == 0  # No data for AI

    def test_get_sentiment_history_empty(self):
        """Test getting sentiment history with no data."""
        service = DatabaseService()
        history = service.get_sentiment_history(days=7)

        # Should still return structure with zeros
        assert "us" in history
        assert len(history["us"]) == 7
        assert all(score == 0 for score in history["us"])

    def test_get_latest_newsletter(self):
        """Test getting the most recent newsletter."""
        service = DatabaseService()

        # Create multiple newsletters
        for i in range(3):
            service.save_newsletter_with_stats(
                source_stats={"us": [], "israel": [], "ai": [], "crypto": []},
                sentiment=f'{{"us": {60 + i}}}',
            )

        latest = service.get_latest_newsletter()
        assert latest is not None
        assert latest.sentiment == '{"us": 62}'  # Last one created

    def test_get_latest_newsletter_empty(self):
        """Test getting latest newsletter when none exist."""
        service = DatabaseService()
        latest = service.get_latest_newsletter()
        assert latest is None

    def test_get_latest_newsletter_with_articles(self):
        """Test getting latest newsletter with articles grouped by category."""
        import json

        service = DatabaseService()

        # Create newsletter with articles
        sources_metadata = {
            "us": [
                {
                    "link": "https://cnbc.com/article1",
                    "source": "CNBC",
                    "text": "US market news",
                    "ai_title": "US Markets Rally",
                }
            ],
            "israel": [
                {
                    "link": "https://globes.co.il/news/123",
                    "source": "Globes",
                    "text": "Israel market news",
                    "ai_title": "Tel Aviv Index Up",
                }
            ],
            "ai": [],
            "crypto": [
                {
                    "link": "https://coindesk.com/btc",
                    "source": "CoinDesk",
                    "text": "Bitcoin news",
                    "ai_title": "Bitcoin Hits New High",
                }
            ],
        }
        service.save_newsletter_with_stats(
            source_stats={"us": [], "israel": [], "ai": [], "crypto": []},
            sources_metadata=sources_metadata,
            sentiment=json.dumps({"us": 65, "israel": 48, "crypto": 72}),
            llm_provider="openai",
        )

        result = service.get_latest_newsletter_with_articles()

        assert result is not None
        assert "newsletter" in result
        assert "sources_metadata" in result
        assert "sentiment" in result
        assert "llm_provider" in result
        assert "created_at" in result

        # Check sources_metadata structure
        assert len(result["sources_metadata"]["us"]) == 1
        assert len(result["sources_metadata"]["israel"]) == 1
        assert len(result["sources_metadata"]["ai"]) == 0
        assert len(result["sources_metadata"]["crypto"]) == 1

        # Check article content
        us_article = result["sources_metadata"]["us"][0]
        assert us_article["source"] == "CNBC"
        assert us_article["ai_title"] == "US Markets Rally"

        # Check sentiment
        assert result["sentiment"]["us"] == 65
        assert result["sentiment"]["israel"] == 48
        assert result["sentiment"]["crypto"] == 72

        # Check llm_provider
        assert result["llm_provider"] == "openai"

    def test_get_latest_newsletter_with_articles_empty(self):
        """Test getting latest newsletter with articles when none exist."""
        service = DatabaseService()
        result = service.get_latest_newsletter_with_articles()
        assert result is None

    def test_get_latest_newsletter_with_articles_no_sentiment(self):
        """Test getting latest newsletter with no sentiment data."""
        service = DatabaseService()

        service.save_newsletter_with_stats(
            source_stats={"us": [], "israel": [], "ai": [], "crypto": []},
            sentiment=None,  # No sentiment
        )

        result = service.get_latest_newsletter_with_articles()
        assert result is not None
        assert result["sentiment"] == {}  # Empty dict, not None


class TestDatabaseErrorHandling:
    """Tests for database error handling."""

    def test_database_error_attributes(self):
        """Test DatabaseError has correct attributes."""
        error = DatabaseError("test_op", "test details")
        assert error.operation == "test_op"
        assert error.details == "test details"
        assert "test_op" in str(error)
        assert "test details" in str(error)


class TestFeedProvider:
    """Tests for FeedProvider model."""

    def test_feed_provider_creation(self):
        """Test creating a feed provider."""
        with session_scope() as session:
            provider = FeedProvider(
                source_name="Yahoo Finance",
                category="us",
                total_runs=3,
                success_count=2,
                reliability=0.67,
            )
            session.add(provider)
            session.commit()
            assert provider.id is not None
            assert provider.total_runs == 3

    def test_feed_provider_to_dict(self):
        """Test feed provider to_dict method."""
        now = datetime.now(timezone.utc)
        provider = FeedProvider(
            id=1,
            source_name="CNBC",
            category="us",
            total_runs=5,
            success_count=4,
            reliability=0.8,
            last_updated=now,
        )
        result = provider.to_dict()
        assert result["source_name"] == "CNBC"
        assert result["category"] == "us"
        assert result["total_runs"] == 5
        assert result["success_count"] == 4
        assert result["reliability"] == 0.8
        assert result["last_updated"] is not None


class TestFeedProviderAggregation:
    """Tests for feed provider stats aggregation."""

    def test_update_feed_providers_creates_new(self):
        """Test update_feed_providers creates new provider record."""
        service = DatabaseService()
        source_stats = {
            "us": [{"name": "Yahoo Finance", "status": "active", "count": 5}],
            "israel": [],
            "ai": [],
            "crypto": [],
        }

        service.update_feed_providers(source_stats)

        with session_scope() as session:
            provider = (
                session.query(FeedProvider)
                .filter_by(
                    source_name="Yahoo Finance",
                    category="us",
                )
                .first()
            )
            assert provider is not None
            assert provider.total_runs == 1
            assert provider.success_count == 1
            assert provider.last_updated is not None

    def test_update_feed_providers_accumulates(self):
        """Test update_feed_providers accumulates stats over time."""
        service = DatabaseService()

        # First update
        service.update_feed_providers(
            {
                "us": [{"name": "CNBC", "status": "active", "count": 3}],
                "israel": [],
                "ai": [],
                "crypto": [],
            }
        )
        # Second update
        service.update_feed_providers(
            {
                "us": [{"name": "CNBC", "status": "active", "count": 7}],
                "israel": [],
                "ai": [],
                "crypto": [],
            }
        )

        with session_scope() as session:
            provider = (
                session.query(FeedProvider)
                .filter_by(
                    source_name="CNBC",
                    category="us",
                )
                .first()
            )
            assert provider.total_runs == 2
            assert provider.success_count == 2

    def test_update_feed_providers_tracks_failures(self):
        """Test update_feed_providers tracks inactive sources."""
        service = DatabaseService()
        source_stats = {
            "us": [{"name": "FT", "status": "inactive", "count": 0}],
            "israel": [],
            "ai": [],
            "crypto": [],
        }

        service.update_feed_providers(source_stats)

        with session_scope() as session:
            provider = (
                session.query(FeedProvider)
                .filter_by(
                    source_name="FT",
                    category="us",
                )
                .first()
            )
            assert provider.total_runs == 1
            assert provider.success_count == 0  # Was inactive

    def test_update_feed_providers_calculates_reliability(self):
        """Test update_feed_providers calculates reliability correctly."""
        service = DatabaseService()

        # First run: active
        service.update_feed_providers(
            {
                "us": [{"name": "TestSource", "status": "active", "count": 5}],
                "israel": [],
                "ai": [],
                "crypto": [],
            }
        )
        # Second run: inactive
        service.update_feed_providers(
            {
                "us": [{"name": "TestSource", "status": "inactive", "count": 0}],
                "israel": [],
                "ai": [],
                "crypto": [],
            }
        )
        # Third run: active
        service.update_feed_providers(
            {
                "us": [{"name": "TestSource", "status": "active", "count": 3}],
                "israel": [],
                "ai": [],
                "crypto": [],
            }
        )

        with session_scope() as session:
            provider = (
                session.query(FeedProvider)
                .filter_by(
                    source_name="TestSource",
                    category="us",
                )
                .first()
            )
            assert provider.total_runs == 3
            assert provider.success_count == 2
            # Reliability = 2/3 = 0.67 (rounded to 2 decimal places)
            assert provider.reliability == 0.67


class TestRetentionCleanup:
    """Tests for retention cleanup."""

    def test_run_retention_cleanup_keeps_recent_newsletters(self):
        """Test cleanup keeps recent newsletters."""
        service = DatabaseService()

        # Create recent newsletter
        service.save_newsletter_with_stats(
            source_stats={"us": [], "israel": [], "ai": [], "crypto": []},
        )

        # Run cleanup
        service.run_retention_cleanup()

        # Recent newsletters should remain
        with session_scope() as session:
            newsletters = session.query(Newsletter).all()
            assert len(newsletters) >= 1


class TestEmailVerification:
    """Tests for email verification methods."""

    def test_create_user_with_email_verified(self):
        """Test creating user with email_verified flag."""
        service = DatabaseService()
        user = service.create_user(
            email="verified@example.com",
            password_hash="hashed_password",
            email_verified=True,
        )
        assert user.email_verified is True

    def test_create_user_default_not_verified(self):
        """Test user is not verified by default."""
        service = DatabaseService()
        user = service.create_user(
            email="unverified@example.com",
            password_hash="hashed_password",
        )
        assert user.email_verified is False

    def test_set_verification_token(self):
        """Test setting verification token."""
        from backend.models.user import User

        service = DatabaseService()
        user = service.create_user(
            email="tokentest@example.com",
            password_hash="hashed_password",
        )

        expires_at = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = service.set_verification_token(user.id, "test_token_123", expires_at)
        assert result is True

        # Verify token was set
        with session_scope() as session:
            updated_user = session.get(User, user.id)
            assert updated_user.verification_token == "test_token_123"
            # SQLite may return naive datetime, so compare without timezone
            stored_expires = updated_user.verification_token_expires_at
            if stored_expires.tzinfo is None:
                stored_expires = stored_expires.replace(tzinfo=timezone.utc)
            assert stored_expires == expires_at

    def test_set_verification_token_nonexistent_user(self):
        """Test setting token for non-existent user returns False."""
        service = DatabaseService()
        expires_at = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = service.set_verification_token(99999, "test_token", expires_at)
        assert result is False

    def test_get_user_by_verification_token(self):
        """Test finding user by verification token."""

        service = DatabaseService()
        user = service.create_user(
            email="findtoken@example.com",
            password_hash="hashed_password",
        )

        expires_at = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
        service.set_verification_token(user.id, "find_me_token", expires_at)

        found_user = service.get_user_by_verification_token("find_me_token")
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == "findtoken@example.com"

    def test_get_user_by_verification_token_not_found(self):
        """Test finding user with non-existent token returns None."""
        service = DatabaseService()
        found_user = service.get_user_by_verification_token("nonexistent_token")
        assert found_user is None

    def test_clear_verification_token(self):
        """Test clearing verification token."""
        from backend.models.user import User

        service = DatabaseService()
        user = service.create_user(
            email="cleartoken@example.com",
            password_hash="hashed_password",
        )

        expires_at = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
        service.set_verification_token(user.id, "clear_me_token", expires_at)

        result = service.clear_verification_token(user.id)
        assert result is True

        with session_scope() as session:
            updated_user = session.get(User, user.id)
            assert updated_user.verification_token is None
            assert updated_user.verification_token_expires_at is None

    def test_mark_email_verified(self):
        """Test marking email as verified."""
        service = DatabaseService()
        user = service.create_user(
            email="markverified@example.com",
            password_hash="hashed_password",
        )

        expires_at = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
        service.set_verification_token(user.id, "verify_token", expires_at)

        verified_user = service.mark_email_verified(user.id)
        assert verified_user is not None
        assert verified_user.email_verified is True
        assert verified_user.verification_token is None
        assert verified_user.verification_token_expires_at is None

    def test_mark_email_verified_nonexistent_user(self):
        """Test marking non-existent user returns None."""
        service = DatabaseService()
        result = service.mark_email_verified(99999)
        assert result is None
