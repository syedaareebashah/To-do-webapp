"""
Database initialization module for the Todo AI Chatbot System.

This module provides functions for initializing the database.
"""

from sqlmodel import SQLModel
from .connection import sync_engine


def init_db():
    """
    Initialize the database by creating all tables.

    This function creates all tables defined in the models if they don't already exist.
    """
    # Import all models to ensure they're registered with SQLModel
    from src.models.user import User
    from src.models.task import Task
    from src.models.conversation import Conversation
    from src.models.message import Message

    # Create all tables
    SQLModel.metadata.create_all(sync_engine)
    print("Database tables created successfully")