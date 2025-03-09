"""
Discount schemas for the 3X-UI Management System.

This module defines Pydantic models for discount data validation and serialization.
"""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, validator

from app.models.discount import DiscountType


# Shared properties
class DiscountBase(BaseModel):
    """
    Base schema for discount data shared between requests.
    """
    code: str = Field(..., min_length=3, max_length=50, description="Discount code")
    description: Optional[str] = Field(None, max_length=500, description="Discount description")
    discount_type: DiscountType = Field(..., description="Discount type (percentage or fixed)")
    value: float = Field(..., gt=0, description="Discount value (percentage or fixed amount)")
    max_uses: Optional[int] = Field(None, gt=0, description="Maximum number of uses")
    min_order_amount: float = Field(0.0, ge=0, description="Minimum order amount to apply")
    max_discount_amount: Optional[float] = Field(None, gt=0, description="Maximum discount amount")
    is_active: bool = Field(True, description="Whether the discount is active")
    starts_at: Optional[datetime] = Field(None, description="When the discount becomes valid")
    expires_at: Optional[datetime] = Field(None, description="When the discount expires")


class DiscountCreate(DiscountBase):
    """
    Schema for creating a new discount.
    """
    @validator("value")
    def validate_value(cls, v, values):
        if "discount_type" in values and values["discount_type"] == DiscountType.PERCENTAGE and v > 100:
            raise ValueError("Percentage discount cannot exceed 100%")
        return v


class DiscountUpdate(BaseModel):
    """
    Schema for updating an existing discount.
    """
    code: Optional[str] = Field(None, min_length=3, max_length=50, description="Discount code")
    description: Optional[str] = Field(None, max_length=500, description="Discount description")
    discount_type: Optional[DiscountType] = Field(None, description="Discount type (percentage or fixed)")
    value: Optional[float] = Field(None, gt=0, description="Discount value (percentage or fixed amount)")
    max_uses: Optional[int] = Field(None, gt=0, description="Maximum number of uses")
    used_count: Optional[int] = Field(None, ge=0, description="Number of times used")
    min_order_amount: Optional[float] = Field(None, ge=0, description="Minimum order amount to apply")
    max_discount_amount: Optional[float] = Field(None, gt=0, description="Maximum discount amount")
    is_active: Optional[bool] = Field(None, description="Whether the discount is active")
    starts_at: Optional[datetime] = Field(None, description="When the discount becomes valid")
    expires_at: Optional[datetime] = Field(None, description="When the discount expires")
    
    @validator("value")
    def validate_value(cls, v, values):
        if v is not None and "discount_type" in values and values["discount_type"] == DiscountType.PERCENTAGE and v > 100:
            raise ValueError("Percentage discount cannot exceed 100%")
        return v


class DiscountInDBBase(DiscountBase):
    """
    Base schema for discounts retrieved from the database.
    """
    id: int
    used_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Discount(DiscountInDBBase):
    """
    Schema for discount data returned to clients.
    """
    is_valid: bool
    orders_count: Optional[int] = Field(0, description="Number of orders using this discount")


class DiscountInDB(DiscountInDBBase):
    """
    Schema for discount data stored in the database.
    """
    pass


class DiscountApply(BaseModel):
    """
    Schema for applying a discount to an order.
    """
    code: str = Field(..., description="Discount code to apply")
    order_amount: float = Field(..., gt=0, description="Order amount to apply discount to")


class DiscountApplyResponse(BaseModel):
    """
    Schema for discount application response.
    """
    is_valid: bool = Field(..., description="Whether the discount is valid")
    discount_amount: float = Field(0.0, description="Discount amount")
    final_amount: float = Field(..., description="Final amount after discount")
    message: Optional[str] = Field(None, description="Message about the discount application") 