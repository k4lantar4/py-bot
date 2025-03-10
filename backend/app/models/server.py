"""
Server model for the 3X-UI Management System.

This module defines the SQLAlchemy ORM model for servers managed by the system.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, JSON, func
from sqlalchemy.orm import relationship

from ..db.session import Base


class Server(Base):
    """
    SQLAlchemy model for servers.
    """
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False, index=True)  # IP or domain
    domain = Column(String, nullable=True)
    port = Column(Integer, nullable=False, default=22)  # SSH port
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    threexui_port = Column(Integer, nullable=False, default=80)  # 3X-UI panel port
    threexui_username = Column(String, nullable=False)
    threexui_password = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    capacity = Column(Integer, nullable=False, default=100)  # Max number of users
    total_bandwidth = Column(Float, nullable=False, default=1000.0)  # Total bandwidth in GB
    used_bandwidth = Column(Float, nullable=False, default=0.0)  # Used bandwidth in GB
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_checked_at = Column(DateTime, nullable=True)
    
    # Relationships
    location = relationship("Location", back_populates="servers")
    services = relationship("Service", back_populates="server")
    
    @property
    def bandwidth_percentage(self) -> float:
        """
        Calculate the percentage of bandwidth used.
        
        Returns:
            Percentage of bandwidth used (0-100)
        """
        if self.total_bandwidth <= 0:
            return 0.0
        return min(100.0, (self.used_bandwidth / self.total_bandwidth) * 100.0)
    
    @property
    def capacity_percentage(self) -> float:
        """
        Calculate the percentage of capacity used. This will be updated by periodic tasks
        that query the 3X-UI API for the current number of users.
        
        Returns:
            Percentage of capacity used (0-100)
        """
        # This would be updated periodically via 3X-UI API
        return 0.0  # Placeholder 