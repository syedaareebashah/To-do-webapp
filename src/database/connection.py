"""
Database connection module for the Todo AI Chatbot System.

This module sets up the database connection using SQLModel and Neon PostgreSQL.
"""

from sqlmodel import create_engine, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import os
from contextlib import contextmanager


# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://username:password@localhost:5432/neon_database"
)


# Create synchronous engine for SQLModel
sync_engine = create_engine(
    DATABASE_URL.replace("+asyncpg", ""),
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for use with dependency injection in FastAPI.

    Yields:
        Session: Database session instance
    """
    with Session(sync_engine) as session:
        yield session


@contextmanager
def get_db_session():
    """
    Context manager for getting a database session.

    Yields:
        Session: Database session instance
    """
    session = Session(sync_engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """
    Initialize the database by creating all tables.
    """
    from src.models import user, task, conversation, message
    from sqlmodel import SQLModel

    # Create all tables defined in the models
    SQLModel.metadata.create_all(sync_engine)