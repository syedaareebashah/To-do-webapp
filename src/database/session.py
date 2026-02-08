"""
Database session management module for the Todo AI Chatbot System.

This module provides utilities for managing database sessions using SQLModel.
"""

from sqlmodel import Session, create_engine
from contextlib import contextmanager
from typing import Generator
import os
from sqlalchemy.pool import QueuePool


# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://username:password@localhost:5432/neon_database"
)


# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL.replace("+asyncpg", ""),  # Use sync driver for SQLModel
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
    with Session(engine) as session:
        yield session


@contextmanager
def get_db_session():
    """
    Context manager for getting a database session.

    Yields:
        Session: Database session instance
    """
    session = Session(engine)
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
    from src.models import User, Task, Conversation, Message
    from sqlmodel import SQLModel

    # Create all tables
    SQLModel.metadata.create_all(bind=engine)