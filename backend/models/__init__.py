"""
Database models for the Capital Market Newsletter application.

This module exports all SQLAlchemy models for use across the application.
"""

from backend.models.base import Base, get_engine, get_session, init_db
from backend.models.newsletter import Newsletter
from backend.models.feed_provider import FeedProvider
from backend.models.article import Article
from backend.models.article_selection import ArticleSelection
from backend.models.user import User
from backend.models.podcast_generation import PodcastGeneration
from backend.models.analytics_report import AnalyticsReport
from backend.models.game_result import GameResult

__all__ = [
    "Base",
    "get_engine",
    "get_session",
    "init_db",
    "Newsletter",
    "FeedProvider",
    "Article",
    "ArticleSelection",
    "User",
    "PodcastGeneration",
    "AnalyticsReport",
    "GameResult",
]
