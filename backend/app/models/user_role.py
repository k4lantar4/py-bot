"""
User-Role association model for the 3X-UI Management System.

This module defines the UserRole model for the database.
"""

from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base_class import Base


class UserRole(Base):
    """
    User-Role association model.
    
    This class represents the many-to-many relationship between users and roles.
    """
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True) 