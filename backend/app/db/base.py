"""
Base module for database models.

This module imports all models to ensure they are registered with SQLAlchemy.
"""

from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.role import Role  # noqa
from app.models.user_role import UserRole  # noqa 