"""
Order and Payment models for the 3X-UI Management System.

This module defines the SQLAlchemy ORM models for orders and payments
in the system.
"""

import enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Enum, func, JSON
from sqlalchemy.orm import relationship

from ..db.session import Base


# Order status enumeration
class OrderStatus(str, enum.Enum):
    """
    Enumeration of order statuses.
    """
    PENDING = "pending"
    AWAITING_PAYMENT = "awaiting_payment"
    PAID = "paid"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"


# Payment method enumeration
class PaymentMethod(str, enum.Enum):
    """
    Enumeration of payment methods.
    """
    CARD = "card"  # Card to card
    ZARINPAL = "zarinpal"
    WALLET = "wallet"  # User's wallet balance


class Order(Base):
    """
    SQLAlchemy model for orders.
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    discount_id = Column(Integer, ForeignKey("discounts.id"), nullable=True)
    
    # Order details
    order_number = Column(String(20), unique=True, index=True, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    amount = Column(Float, nullable=False)  # Original amount
    discount_amount = Column(Float, default=0.0)  # Discount amount
    final_amount = Column(Float, nullable=False)  # Final amount after discount
    
    # Order metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, nullable=True)  # When order expires if not paid
    completed_at = Column(DateTime, nullable=True)  # When order was completed
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    discount = relationship("Discount", back_populates="orders")
    payments = relationship("Payment", back_populates="order")
    
    # Additional information
    metadata = Column(JSON, nullable=True)
    is_test = Column(Boolean, default=False)
    
    def __str__(self) -> str:
        """String representation of order."""
        return f"Order {self.order_number} ({self.status})"
    
    @property
    def is_paid(self) -> bool:
        """
        Check if the order is paid.
        
        Returns:
            True if the order is paid, False otherwise
        """
        return self.status in (OrderStatus.PAID, OrderStatus.COMPLETED)
    
    @property
    def is_active(self) -> bool:
        """
        Check if the order is active (not cancelled or failed).
        
        Returns:
            True if the order is active, False otherwise
        """
        return self.status not in (OrderStatus.CANCELLED, OrderStatus.FAILED)
    
    @property
    def is_expired(self) -> bool:
        """
        Check if the order is expired.
        
        Returns:
            True if the order is expired, False otherwise
        """
        if not self.expires_at:
            return False
        return self.expires_at < func.now() and self.status == OrderStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """Check if order is completed."""
        return self.status == OrderStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.status == OrderStatus.CANCELLED

    @property
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled."""
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.AWAITING_PAYMENT,
        ]

    @property
    def can_be_refunded(self) -> bool:
        """Check if order can be refunded."""
        return self.status in [
            OrderStatus.PAID,
            OrderStatus.PROCESSING,
            OrderStatus.COMPLETED,
        ]


class Payment(Base):
    """
    SQLAlchemy model for payments.
    """
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment details
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    transaction_id = Column(String, nullable=True)  # External transaction ID
    payment_status = Column(String, nullable=False, default="pending")
    
    # Payment metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Payment provider details
    provider_data = Column(Text, nullable=True)  # JSON data from payment provider
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    user = relationship("User", back_populates="payments")
    
    @property
    def is_successful(self) -> bool:
        """
        Check if the payment was successful.
        
        Returns:
            True if the payment was successful, False otherwise
        """
        return self.payment_status == "completed" 