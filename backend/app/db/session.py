"""
Database session management module.

This module initializes and manages the SQLAlchemy session for database operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create the SQLAlchemy engine
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,  # Ping the server before connections to ensure they're valid
    pool_recycle=3600,   # Recycle connections after an hour to avoid stale connections
    pool_size=20,        # Maximum number of connections to keep in the pool
    max_overflow=10,     # Maximum number of connections to create beyond pool_size
)

# Create a sessionmaker with autocommit=False (transactions must be explicitly committed)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for SQLAlchemy models
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