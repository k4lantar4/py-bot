"""
Service model for the 3X-UI Management System.

This module defines the SQLAlchemy ORM model for services (subscription plans)
offered by the system.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, JSON, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Service(Base):
    """
    SQLAlchemy model for services (subscription plans).
    """
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    inbound_id = Column(Integer, nullable=True)  # ID of the inbound in 3X-UI
    protocol = Column(String, nullable=False)  # vless, vmess, trojan, etc.
    price = Column(Float, nullable=False)
    traffic = Column(Float, nullable=False)  # Traffic in GB
    duration = Column(Integer, nullable=False)  # Duration in days
    concurrent_connections = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    settings = Column(JSON, nullable=True)  # Additional settings specific to the protocol
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    server = relationship("Server", back_populates="services")
    orders = relationship("Order", back_populates="service")
    
    @property
    def price_per_gb(self) -> float:
        """
        Calculate the price per GB of traffic.
        
        Returns:
            Price per GB of traffic
        """
        if self.traffic <= 0:
            return 0.0
        return self.price / self.traffic
    
    @property
    def price_per_month(self) -> float:
        """
        Calculate the monthly price equivalent.
        
        Returns:
            Price per month
        """
        if self.duration <= 0:
            return 0.0
        return (self.price / self.duration) * 30 