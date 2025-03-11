"""
User model for the 3X-UI Management System.

This module defines the User model for the database.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, ForeignKey, func, Text, BigInteger
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class User(Base):
    """
    User model.
    
    This class represents a user in the system.
    """
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    language = Column(String(2), default="fa")
    timezone = Column(String(50), default="Asia/Tehran")
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    balance = Column(Integer, default=0)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    last_login = Column(DateTime, nullable=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    wallet_balance = Column(Float, default=0.0)
    
    # Relationships
    roles = relationship("Role", secondary="user_role", back_populates="users")
    orders = relationship("Order", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    accounts = relationship("VirtualAccount", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")
    
    @property
    def role_names(self) -> List[str]:
        """
        Get role names.
        
        Returns:
            List[str]: List of role names
        """
        return [role.name for role in self.roles]

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return True if self.telegram_id or self.hashed_password else False

    @property
    def display_name(self) -> str:
        """Get user's display name."""
        return self.full_name or self.username or f"User {self.id}"

    def get_id(self) -> str:
        """Get user ID as string."""
        return str(self.id)

    def __str__(self) -> str:
        """String representation of user."""
        return f"{self.display_name} ({self.id})"


class UserClient(Base):
    """
    SQLAlchemy model for user clients created in 3X-UI panels.
    """
    __tablename__ = "user_clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    client_id = Column(String, nullable=False)  # Client ID in 3X-UI
    email = Column(String, nullable=False)  # Client email/name in 3X-UI
    subscription_url = Column(String, nullable=True)  # Subscription URL
    total_traffic = Column(Float, nullable=False)  # Total traffic in GB
    used_traffic = Column(Float, default=0.0)  # Used traffic in GB
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_checked_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="clients")
    service = relationship("Service", back_populates="clients")
    
    @property
    def traffic_percentage(self) -> float:
        """
        Calculate the percentage of traffic used.
        
        Returns:
            Percentage of traffic used (0-100)
        """
        if self.total_traffic <= 0:
            return 0.0
        return min(100.0, (self.used_traffic / self.total_traffic) * 100.0)
    
    @property
    def has_expired(self) -> bool:
        """
        Check if the client has expired.
        
        Returns:
            True if expired, False otherwise
        """
        if not self.expiry_date:
            return False
        return self.expiry_date < func.now()


# Add relationships after class definition to avoid circular imports
User.clients = relationship("UserClient", back_populates="user") 