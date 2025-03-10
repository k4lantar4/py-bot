"""
Role model for the 3X-UI Management System.

This module defines the Role model for the database.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class Role(Base):
    """
    Role model.
    
    This class represents a role in the system.
    """
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    users = relationship("User", secondary="user_role", back_populates="roles") 