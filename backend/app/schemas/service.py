"""
Service schemas for the 3X-UI Management System.

This module defines Pydantic models for service data validation and serialization.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from pydantic import BaseModel, Field, validator


# Shared properties
class ServiceBase(BaseModel):
    """
    Base schema for service data shared between requests.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Service name")
    server_id: int = Field(..., gt=0, description="ID of the server providing this service")
    protocol: str = Field(..., description="Protocol (vless, vmess, trojan, etc.)")
    price: float = Field(..., gt=0, description="Service price")
    traffic: float = Field(..., gt=0, description="Traffic in GB")
    duration: int = Field(..., gt=0, description="Duration in days")
    concurrent_connections: int = Field(1, ge=1, description="Maximum concurrent connections")
    is_active: bool = Field(True, description="Whether the service is active")
    description: Optional[str] = Field(None, max_length=1000, description="Service description")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing service")


# Properties to receive on service creation
class ServiceCreate(ServiceBase):
    """
    Schema for creating a new service.
    """
    inbound_id: Optional[int] = Field(None, description="ID of the inbound in 3X-UI panel")
    settings: Optional[Dict[str, Any]] = Field(None, description="Additional protocol-specific settings")


# Properties to receive on service update
class ServiceUpdate(BaseModel):
    """
    Schema for updating an existing service.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Service name")
    server_id: Optional[int] = Field(None, gt=0, description="ID of the server providing this service")
    inbound_id: Optional[int] = Field(None, description="ID of the inbound in 3X-UI panel")
    protocol: Optional[str] = Field(None, description="Protocol (vless, vmess, trojan, etc.)")
    price: Optional[float] = Field(None, gt=0, description="Service price")
    traffic: Optional[float] = Field(None, gt=0, description="Traffic in GB")
    duration: Optional[int] = Field(None, gt=0, description="Duration in days")
    concurrent_connections: Optional[int] = Field(None, ge=1, description="Maximum concurrent connections")
    is_active: Optional[bool] = Field(None, description="Whether the service is active")
    description: Optional[str] = Field(None, max_length=1000, description="Service description")
    settings: Optional[Dict[str, Any]] = Field(None, description="Additional protocol-specific settings")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing service")


# Properties shared by models stored in DB
class ServiceInDBBase(ServiceBase):
    """
    Base schema for services retrieved from the database.
    """
    id: int
    inbound_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Properties to return to client
class Service(ServiceInDBBase):
    """
    Schema for service data returned to clients.
    """
    server_name: Optional[str] = Field(None, description="Name of the server")
    price_per_gb: float = Field(..., description="Price per GB of traffic")
    price_per_month: float = Field(..., description="Monthly price equivalent")
    users_count: Optional[int] = Field(0, description="Number of users using this service")


# Properties stored in DB
class ServiceInDB(ServiceInDBBase):
    """
    Schema for service data stored in the database.
    """
    pass


# Schema for service protocol settings
class ServiceProtocolSettings(BaseModel):
    """
    Schema for service protocol-specific settings.
    """
    class Config:
        extra = "allow"  # Allow extra fields for flexibility


# Schema for service statistics
class ServiceStats(BaseModel):
    """
    Schema for service statistics data.
    """
    total_orders: int = Field(0, description="Total number of orders for this service")
    active_orders: int = Field(0, description="Number of active orders for this service")
    total_revenue: float = Field(0.0, description="Total revenue from this service")
    monthly_revenue: float = Field(0.0, description="Monthly revenue from this service")
    users_count: int = Field(0, description="Number of users using this service")
    
    class Config:
        from_attributes = True 