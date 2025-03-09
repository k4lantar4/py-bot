"""
Order and Payment schemas for the 3X-UI Management System.

This module defines Pydantic models for order and payment data validation and serialization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, validator

from app.models.order import OrderStatus, PaymentMethod


# Order schemas
class OrderBase(BaseModel):
    """
    Base schema for order data shared between requests.
    """
    user_id: int = Field(..., gt=0, description="User ID")
    service_id: int = Field(..., gt=0, description="Service ID")
    discount_id: Optional[int] = Field(None, gt=0, description="Discount ID")
    amount: float = Field(..., gt=0, description="Original order amount")
    notes: Optional[str] = Field(None, description="Order notes")


class OrderCreate(OrderBase):
    """
    Schema for creating a new order.
    """
    pass


class OrderUpdate(BaseModel):
    """
    Schema for updating an existing order.
    """
    status: Optional[OrderStatus] = Field(None, description="Order status")
    discount_id: Optional[int] = Field(None, gt=0, description="Discount ID")
    discount_amount: Optional[float] = Field(None, ge=0, description="Discount amount")
    final_amount: Optional[float] = Field(None, gt=0, description="Final amount after discount")
    notes: Optional[str] = Field(None, description="Order notes")


class OrderInDBBase(OrderBase):
    """
    Base schema for orders retrieved from the database.
    """
    id: int
    order_number: str
    status: OrderStatus
    discount_amount: float
    final_amount: float
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Order(OrderInDBBase):
    """
    Schema for order data returned to clients.
    """
    is_paid: bool
    is_active: bool
    is_expired: bool
    user_email: Optional[str] = Field(None, description="Email of the user")
    service_name: Optional[str] = Field(None, description="Name of the service")
    discount_code: Optional[str] = Field(None, description="Discount code")
    payments: Optional[List["Payment"]] = Field([], description="Order payments")


class OrderInDB(OrderInDBBase):
    """
    Schema for order data stored in the database.
    """
    pass


# Payment schemas
class PaymentBase(BaseModel):
    """
    Base schema for payment data shared between requests.
    """
    order_id: int = Field(..., gt=0, description="Order ID")
    user_id: int = Field(..., gt=0, description="User ID")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field("USD", description="Payment currency")
    notes: Optional[str] = Field(None, description="Payment notes")


class PaymentCreate(PaymentBase):
    """
    Schema for creating a new payment.
    """
    transaction_id: Optional[str] = Field(None, description="External transaction ID")
    provider_data: Optional[str] = Field(None, description="JSON data from payment provider")


class PaymentUpdate(BaseModel):
    """
    Schema for updating an existing payment.
    """
    payment_status: Optional[str] = Field(None, description="Payment status")
    transaction_id: Optional[str] = Field(None, description="External transaction ID")
    processed_at: Optional[datetime] = Field(None, description="When the payment was processed")
    notes: Optional[str] = Field(None, description="Payment notes")
    provider_data: Optional[str] = Field(None, description="JSON data from payment provider")


class PaymentInDBBase(PaymentBase):
    """
    Base schema for payments retrieved from the database.
    """
    id: int
    payment_status: str
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Payment(PaymentInDBBase):
    """
    Schema for payment data returned to clients.
    """
    is_successful: bool
    user_email: Optional[str] = Field(None, description="Email of the user")
    order_number: Optional[str] = Field(None, description="Order number")


class PaymentInDB(PaymentInDBBase):
    """
    Schema for payment data stored in the database.
    """
    provider_data: Optional[str] = None


# Order statistics schema
class OrderStats(BaseModel):
    """
    Schema for order statistics data.
    """
    total_orders: int = Field(0, description="Total number of orders")
    pending_orders: int = Field(0, description="Number of pending orders")
    completed_orders: int = Field(0, description="Number of completed orders")
    cancelled_orders: int = Field(0, description="Number of cancelled orders")
    total_revenue: float = Field(0.0, description="Total revenue")
    monthly_revenue: float = Field(0.0, description="Monthly revenue")
    
    class Config:
        from_attributes = True


# Make sure schemas are available in the right order
from pydantic import create_model
# Avoid circular imports
Payment.update_forward_refs() 