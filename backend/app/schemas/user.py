"""
User schemas for the 3X-UI Management System.

This module defines Pydantic models for user data validation and serialization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, validator


# Shared properties
class UserBase(BaseModel):
    """
    Base schema for user data shared between requests.
    """
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    is_active: bool = Field(True, description="Whether the user is active")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    telegram_id: Optional[str] = Field(None, description="Telegram user ID")
    language: Optional[str] = Field("en", min_length=2, max_length=5, description="User preferred language")


# Properties to receive on user creation
class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str = Field(..., min_length=8, description="Password")
    is_superuser: bool = Field(False, description="Whether the user is a superuser")
    roles: List[str] = Field(["customer"], description="User roles")


# Properties to receive on user update
class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    """
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    password: Optional[str] = Field(None, min_length=8, description="Password")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    is_superuser: Optional[bool] = Field(None, description="Whether the user is a superuser")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    telegram_id: Optional[str] = Field(None, description="Telegram user ID")
    wallet_balance: Optional[float] = Field(None, ge=0, description="User wallet balance")
    language: Optional[str] = Field(None, min_length=2, max_length=5, description="User preferred language")
    roles: Optional[List[str]] = Field(None, description="User roles")
    settings: Optional[Dict[str, Any]] = Field(None, description="User preferences and settings")


# Properties to receive on wallet update
class WalletUpdate(BaseModel):
    """
    Schema for updating a user's wallet balance.
    """
    amount: float = Field(..., description="Amount to add to or subtract from wallet")
    operation: str = Field(..., description="Operation to perform (add or subtract)")
    description: Optional[str] = Field(None, description="Description of the transaction")
    
    @validator("operation")
    def validate_operation(cls, v):
        if v not in ["add", "subtract"]:
            raise ValueError("Operation must be either 'add' or 'subtract'")
        return v


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    """
    Base schema for users retrieved from the database.
    """
    id: int
    is_superuser: bool
    is_verified: bool
    totp_enabled: bool
    wallet_balance: float
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# Properties to return to client
class User(UserInDBBase):
    """
    Schema for user data returned to clients.
    """
    roles: List[str] = Field([], description="User roles")
    clients_count: Optional[int] = Field(0, description="Number of clients")
    orders_count: Optional[int] = Field(0, description="Number of orders")


# Properties stored in DB
class UserInDB(UserInDBBase):
    """
    Schema for user data stored in the database (including hashed password).
    """
    hashed_password: str
    totp_secret: Optional[str] = None


# Schema for user roles
class UserRoleUpdate(BaseModel):
    """
    Schema for updating user roles.
    """
    roles: List[str] = Field(..., description="List of role names")
    
    @validator("roles")
    def validate_roles(cls, v):
        valid_roles = ["admin", "manager", "vendor", "customer", "guest"]
        for role in v:
            if role not in valid_roles:
                raise ValueError(f"Invalid role: {role}. Must be one of {valid_roles}")
        return v


# Schema for user client
class UserClientBase(BaseModel):
    """
    Base schema for user client data.
    """
    user_id: int = Field(..., gt=0, description="User ID")
    service_id: int = Field(..., gt=0, description="Service ID")
    client_id: str = Field(..., description="Client ID in 3X-UI")
    email: str = Field(..., description="Client email/name in 3X-UI")
    subscription_url: Optional[str] = Field(None, description="Subscription URL")
    total_traffic: float = Field(..., gt=0, description="Total traffic in GB")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")
    is_active: bool = Field(True, description="Whether the client is active")


class UserClientCreate(UserClientBase):
    """
    Schema for creating a new user client.
    """
    pass


class UserClientUpdate(BaseModel):
    """
    Schema for updating an existing user client.
    """
    email: Optional[str] = Field(None, description="Client email/name in 3X-UI")
    subscription_url: Optional[str] = Field(None, description="Subscription URL")
    total_traffic: Optional[float] = Field(None, gt=0, description="Total traffic in GB")
    used_traffic: Optional[float] = Field(None, ge=0, description="Used traffic in GB")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")
    is_active: Optional[bool] = Field(None, description="Whether the client is active")


class UserClientInDBBase(UserClientBase):
    """
    Base schema for user clients retrieved from the database.
    """
    id: int
    used_traffic: float
    created_at: datetime
    updated_at: datetime
    last_checked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserClient(UserClientInDBBase):
    """
    Schema for user client data returned to clients.
    """
    traffic_percentage: float = Field(..., description="Percentage of traffic used")
    has_expired: bool = Field(..., description="Whether the client has expired")
    service_name: Optional[str] = Field(None, description="Name of the service")
    user_email: Optional[str] = Field(None, description="Email of the user")


class UserClientInDB(UserClientInDBBase):
    """
    Schema for user client data stored in the database.
    """
    pass 