"""
Database session module for the 3X-UI Management System.

This module provides the SQLAlchemy session for the application.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os

from ..core.config import settings

# Get database URL from environment variable or use default
DATABASE_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://user:password@db/threexui")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    poolclass=QueuePool,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    echo=settings.DEBUG,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


# Dependency function to get a database session
def get_db() -> Session:
    """
    Get a database session dependency for FastAPI routes.
    
    Yields:
        An SQLAlchemy session
        
    Note:
        The session is automatically closed after the request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_database():
    """Set up database tables and initial data."""
    from ..models.base import Base

    # Create all tables
    Base.metadata.create_all(bind=engine) 