"""
Database initialization module for the 3X-UI Management System.

This module provides functions for initializing the database.
"""

import logging
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.utils.logger import logger


def init_db(db: Session) -> None:
    """
    Initialize the database.
    
    Args:
        db: SQLAlchemy session
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Create first superuser if it doesn't exist
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_active=True,
            full_name="System Administrator",
            roles=["admin"],
        )
        user = crud.user.create(db, obj_in=user_in)
        logger.info(f"First superuser created: {user.username}")
    else:
        logger.info(f"Superuser already exists: {user.username}")
    
    # Create default roles if they don't exist
    create_default_roles(db)


def create_default_roles(db: Session) -> None:
    """
    Create default roles.
    
    Args:
        db: SQLAlchemy session
    """
    default_roles = [
        {"name": "admin", "description": "Administrator with full access"},
        {"name": "manager", "description": "Manager with limited administrative access"},
        {"name": "user", "description": "Regular user with basic access"},
        {"name": "reseller", "description": "Reseller with client management access"},
        {"name": "support", "description": "Support staff with limited access"},
    ]
    
    for role_data in default_roles:
        role = crud.role.get_by_name(db, name=role_data["name"])
        if not role:
            role_in = schemas.RoleCreate(
                name=role_data["name"],
                description=role_data["description"],
            )
            role = crud.role.create(db, obj_in=role_in)
            logger.info(f"Role created: {role.name}")
        else:
            logger.info(f"Role already exists: {role.name}") 