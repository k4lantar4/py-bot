"""
User schemas for the 3X-UI Management System.

This module defines the schemas for user data validation and serialization.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, validator


# Shared properties
class UserBase(BaseModel):
    """
    Base schema for user data shared between requests.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    telegram_id: Optional[str] = Field(None, description="Telegram user ID")
    language: Optional[str] = Field("en", min_length=2, max_length=5, description="User preferred language")


# Properties to receive on user creation
class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    roles: Optional[List[str]] = Field(default_factory=lambda: ["user"])

    @validator("username")
    def username_alphanumeric(cls, v):
        """Validate that username is alphanumeric with optional underscores."""
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError("Username must be alphanumeric with optional underscores")
        return v


# Properties to receive on user update
class UserUpdate(UserBase):
    """
    Schema for updating an existing user.
    """
    password: Optional[str] = None
    roles: Optional[List[str]] = None
    is_superuser: Optional[bool] = None
    telegram_id: Optional[str] = None
    wallet_balance: Optional[float] = None
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    language: Optional[str] = Field(None, min_length=2, max_length=5, description="User preferred language")


# Properties to receive on wallet update
class WalletUpdate(BaseModel):
    """
    Schema for updating a user's wallet balance.
    """
    amount: float = Field(..., gt=0.0, description="Amount to add or subtract")
    operation: str = Field(..., description="Operation to perform: 'add' or 'subtract'")

    @validator("operation")
    def validate_operation(cls, v):
        """Validate that operation is either 'add' or 'subtract'."""
        if v not in ["add", "subtract"]:
            raise ValueError("Operation must be either 'add' or 'subtract'")
        return v


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    """
    Base schema for users retrieved from the database.
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    telegram_id: Optional[str] = None
    wallet_balance: float = 0.0
    role_names: List[str] = []

    class Config:
        orm_mode = True


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
    roles: List[str]
    
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