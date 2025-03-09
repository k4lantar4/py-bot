"""
User model for the 3X-UI Management System.

This module defines the SQLAlchemy ORM model for users of the system,
including authentication and role-based access control.
"""

import enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Enum, JSON, func, Table
from sqlalchemy.orm import relationship

from app.db.session import Base


# User role enumeration
class UserRole(str, enum.Enum):
    """
    Enumeration of user roles for role-based access control.
    """
    ADMIN = "admin"
    MANAGER = "manager"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    GUEST = "guest"


# User-role association table for many-to-many relationship
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role", String, primary_key=True),
)


class User(Base):
    """
    SQLAlchemy model for users.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Two-factor authentication
    totp_secret = Column(String, nullable=True)  # TOTP secret for 2FA
    totp_enabled = Column(Boolean, default=False)
    
    # Contact information
    phone = Column(String, nullable=True)
    telegram_id = Column(String, nullable=True, unique=True)
    
    # Financial information
    wallet_balance = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Preferences and settings
    settings = Column(JSON, nullable=True)
    language = Column(String, default="en")
    
    # Relationships
    roles = relationship("UserRole", secondary=user_roles, collection_class=list)
    orders = relationship("Order", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    
    def has_role(self, role: str) -> bool:
        """
        Check if the user has a specific role.
        
        Args:
            role: The role to check
            
        Returns:
            True if the user has the role, False otherwise
        """
        if self.is_superuser:
            return True
        return role in self.roles
    
    @property
    def role_names(self) -> List[str]:
        """
        Get the role names of the user.
        
        Returns:
            List of role names
        """
        return [role.value for role in self.roles]


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