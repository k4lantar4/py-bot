#!/usr/bin/env python3
"""
Database initialization script for the 3X-UI Management System.

This script initializes the database, creates tables, and adds initial data.
"""

import logging
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.exc import SQLAlchemyError
import emoji

from app.db.session import engine, Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Location, User, UserRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("init_db")


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info(f"{emoji.emojize(':check_mark:')} Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"{emoji.emojize(':cross_mark:')} Error creating database tables: {e}")
        sys.exit(1)


def create_initial_data() -> None:
    """
    Create initial data in the database.
    """
    from sqlalchemy.orm import Session
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    try:
        # Create initial locations
        locations = [
            Location(
                name="United States",
                country="United States",
                country_code="US",
                flag_emoji="🇺🇸",
                is_active=True
            ),
            Location(
                name="Germany",
                country="Germany",
                country_code="DE",
                flag_emoji="🇩🇪",
                is_active=True
            ),
            Location(
                name="Singapore",
                country="Singapore",
                country_code="SG",
                flag_emoji="🇸🇬",
                is_active=True
            ),
        ]
        
        # Check if locations already exist
        existing_locations = db.query(Location).count()
        if existing_locations == 0:
            db.add_all(locations)
            db.commit()
            logger.info(f"{emoji.emojize(':check_mark:')} Initial locations created")
        else:
            logger.info(f"{emoji.emojize(':information:')} Locations already exist, skipping creation")
        
        # Create superuser if it doesn't exist
        superuser_exists = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        if not superuser_exists:
            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_active=True,
                is_superuser=True,
                is_verified=True,
                wallet_balance=0.0,
            )
            db.add(superuser)
            db.commit()
            
            # Add admin role to superuser
            db.execute(
                "INSERT INTO user_roles (user_id, role) VALUES (:user_id, :role)",
                {"user_id": superuser.id, "role": UserRole.ADMIN.value}
            )
            db.commit()
            
            logger.info(f"{emoji.emojize(':check_mark:')} Superuser created with email: {settings.FIRST_SUPERUSER_EMAIL}")
        else:
            logger.info(f"{emoji.emojize(':information:')} Superuser already exists, skipping creation")
        
    except SQLAlchemyError as e:
        logger.error(f"{emoji.emojize(':cross_mark:')} Error creating initial data: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def main() -> None:
    """
    Main function to initialize the database.
    """
    logger.info(f"{emoji.emojize(':rocket:')} Starting database initialization")
    
    # Initialize database
    init_db()
    
    # Create initial data
    create_initial_data()
    
    logger.info(f"{emoji.emojize(':sparkles:')} Database initialization completed successfully")


if __name__ == "__main__":
    main() 