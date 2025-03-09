"""
Server schemas for the 3X-UI Management System.

This module defines Pydantic models for server data validation and serialization.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, validator, AnyHttpUrl


# Shared properties
class ServerBase(BaseModel):
    """
    Base schema for server data shared between requests.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Server name")
    address: str = Field(..., min_length=2, max_length=255, description="Server address (IP or domain)")
    domain: Optional[str] = Field(None, min_length=3, max_length=255, description="Server domain for services")
    port: int = Field(22, ge=1, le=65535, description="SSH port")
    threexui_port: int = Field(80, ge=1, le=65535, description="3X-UI panel port")
    location_id: int = Field(..., gt=0, description="ID of the location where server is hosted")
    capacity: int = Field(100, ge=1, description="Maximum number of users")
    total_bandwidth: float = Field(1000.0, gt=0, description="Total bandwidth in GB")
    is_active: bool = Field(True, description="Whether the server is active")
    description: Optional[str] = Field(None, max_length=1000, description="Server description")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing server")


# Properties to receive on server creation
class ServerCreate(ServerBase):
    """
    Schema for creating a new server.
    """
    username: str = Field(..., min_length=1, max_length=100, description="SSH username")
    password: str = Field(..., min_length=1, description="SSH password")
    threexui_username: str = Field(..., min_length=1, max_length=100, description="3X-UI panel username")
    threexui_password: str = Field(..., min_length=1, description="3X-UI panel password")


# Properties to receive on server update
class ServerUpdate(BaseModel):
    """
    Schema for updating an existing server.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Server name")
    address: Optional[str] = Field(None, min_length=2, max_length=255, description="Server address (IP or domain)")
    domain: Optional[str] = Field(None, min_length=3, max_length=255, description="Server domain for services")
    port: Optional[int] = Field(None, ge=1, le=65535, description="SSH port")
    username: Optional[str] = Field(None, min_length=1, max_length=100, description="SSH username")
    password: Optional[str] = Field(None, min_length=1, description="SSH password")
    threexui_port: Optional[int] = Field(None, ge=1, le=65535, description="3X-UI panel port")
    threexui_username: Optional[str] = Field(None, min_length=1, max_length=100, description="3X-UI panel username")
    threexui_password: Optional[str] = Field(None, min_length=1, description="3X-UI panel password")
    location_id: Optional[int] = Field(None, gt=0, description="ID of the location where server is hosted")
    capacity: Optional[int] = Field(None, ge=1, description="Maximum number of users")
    total_bandwidth: Optional[float] = Field(None, gt=0, description="Total bandwidth in GB")
    used_bandwidth: Optional[float] = Field(None, ge=0, description="Used bandwidth in GB")
    is_active: Optional[bool] = Field(None, description="Whether the server is active")
    description: Optional[str] = Field(None, max_length=1000, description="Server description")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing server")


# Properties shared by models stored in DB
class ServerInDBBase(ServerBase):
    """
    Base schema for servers retrieved from the database.
    """
    id: int
    used_bandwidth: float
    created_at: datetime
    updated_at: datetime
    last_checked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Properties to return to client
class Server(ServerInDBBase):
    """
    Schema for server data returned to clients.
    """
    bandwidth_percentage: float = Field(0.0, description="Percentage of bandwidth used")
    capacity_percentage: float = Field(0.0, description="Percentage of capacity used")
    location_name: Optional[str] = Field(None, description="Name of the location")
    status: Optional[Dict[str, Any]] = Field(None, description="Server status information")


# Properties stored in DB
class ServerInDB(ServerInDBBase):
    """
    Schema for server data stored in the database (including sensitive fields).
    """
    username: str
    password: str
    threexui_username: str
    threexui_password: str


# Schema for server status
class ServerStatus(BaseModel):
    """
    Schema for server status data.
    """
    is_online: bool = Field(..., description="Whether the server is online")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    checked_at: datetime = Field(..., description="When the status was checked")
    error: Optional[str] = Field(None, description="Error message if any")


# Schema for server statistics
class ServerStats(BaseModel):
    """
    Schema for server statistics data.
    """
    total_users: int = Field(0, description="Total number of users")
    active_users: int = Field(0, description="Number of active users")
    total_bandwidth: float = Field(0.0, description="Total bandwidth capacity in GB")
    used_bandwidth: float = Field(0.0, description="Used bandwidth in GB")
    bandwidth_percentage: float = Field(0.0, description="Percentage of bandwidth used")
    uptime_percentage: float = Field(0.0, description="Server uptime percentage")
    uptime_days: float = Field(0.0, description="Server uptime in days")
    
    class Config:
        from_attributes = True 