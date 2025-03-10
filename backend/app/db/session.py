"""
Database session module for the 3X-UI Management System.

This module provides the SQLAlchemy session for the application.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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