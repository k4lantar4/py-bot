"""
Discount model for the 3X-UI Management System.

This module defines the SQLAlchemy ORM model for discount codes
that can be applied to orders.
"""

import enum
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Enum, func
from sqlalchemy.orm import relationship

from app.db.session import Base


# Discount type enumeration
class DiscountType(str, enum.Enum):
    """
    Enumeration of discount types.
    """
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Discount(Base):
    """
    SQLAlchemy model for discount codes.
    """
    __tablename__ = "discounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    discount_type = Column(Enum(DiscountType), nullable=False)
    value = Column(Float, nullable=False)  # Percentage or fixed amount
    max_uses = Column(Integer, nullable=True)  # Maximum number of uses (null for unlimited)
    used_count = Column(Integer, default=0)  # Number of times used
    min_order_amount = Column(Float, default=0.0)  # Minimum order amount to apply
    max_discount_amount = Column(Float, nullable=True)  # Maximum discount amount (for percentage discounts)
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime, nullable=True)  # When the discount becomes valid
    expires_at = Column(DateTime, nullable=True)  # When the discount expires
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="discount")
    
    @property
    def is_valid(self) -> bool:
        """
        Check if the discount is currently valid.
        
        Returns:
            True if the discount is valid, False otherwise
        """
        now = func.now()
        
        # Check if active
        if not self.is_active:
            return False
        
        # Check start date
        if self.starts_at and self.starts_at > now:
            return False
        
        # Check expiration date
        if self.expires_at and self.expires_at < now:
            return False
        
        # Check usage limit
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        
        return True
    
    def calculate_discount_amount(self, order_amount: float) -> float:
        """
        Calculate the discount amount for an order.
        
        Args:
            order_amount: The order amount
            
        Returns:
            The discount amount
        """
        # Check minimum order amount
        if order_amount < self.min_order_amount:
            return 0.0
        
        if self.discount_type == DiscountType.FIXED:
            return min(self.value, order_amount)
        
        # Percentage discount
        discount_amount = order_amount * (self.value / 100.0)
        
        # Apply maximum discount amount if set
        if self.max_discount_amount is not None:
            discount_amount = min(discount_amount, self.max_discount_amount)
        
        return discount_amount 