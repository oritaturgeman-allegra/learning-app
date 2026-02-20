"""
Database base configuration and session management.

Provides SQLAlchemy engine, session factory, and base model class.
Uses SQLite for development, easily switchable to PostgreSQL for production.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.config import config


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Use centralized configuration for database settings
DATABASE_URL = config.database_url

# Handle SQLite-specific configuration
_is_sqlite = DATABASE_URL.startswith("sqlite")

# Create engine with appropriate settings
if _is_sqlite:
    # SQLite: use StaticPool for thread safety, check_same_thread=False for Flask
    _engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=config.sql_echo,
    )
else:
    # PostgreSQL/other: use connection pooling
    _engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before use
        echo=config.sql_echo,
    )

# Session factory
SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def get_engine():
    """Get the SQLAlchemy engine instance."""
    return _engine


def get_session() -> Session:
    """
    Get a new database session.

    Returns:
        Session: A new SQLAlchemy session

    Note:
        Caller is responsible for closing the session.
        Prefer using session_scope() context manager instead.
    """
    return SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Usage:
        with session_scope() as session:
            session.add(newsletter)
            # auto-commits on success, rolls back on exception

    Yields:
        Session: A database session that auto-commits/rollbacks
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called once at application startup.
    For production, use Alembic migrations instead.
    """
    # Ensure data directory exists for SQLite
    if _is_sqlite:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    Base.metadata.create_all(bind=_engine)
