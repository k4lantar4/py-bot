"""
Location model for the 3X-UI Management System.

This module defines the SQLAlchemy ORM model for locations where servers are hosted.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from ..db.session import Base


class Location(Base):
    """
    SQLAlchemy model for locations.
    """
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False, index=True)
    country_code = Column(String(2), nullable=False)  # ISO 3166-1 alpha-2 code
    flag_emoji = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    servers = relationship("Server", back_populates="location") 