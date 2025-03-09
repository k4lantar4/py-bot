"""
Location schemas for the 3X-UI Management System.

This module defines Pydantic models for location data validation and serialization.
"""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


# Shared properties
class LocationBase(BaseModel):
    """
    Base schema for location data shared between requests.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Location name")
    country: str = Field(..., min_length=2, max_length=100, description="Country name")
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    flag_emoji: Optional[str] = Field(None, description="Flag emoji for the country")
    is_active: bool = Field(True, description="Whether the location is active")


# Properties to receive on location creation
class LocationCreate(LocationBase):
    """
    Schema for creating a new location.
    """
    pass


# Properties to receive on location update
class LocationUpdate(BaseModel):
    """
    Schema for updating an existing location.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Location name")
    country: Optional[str] = Field(None, min_length=2, max_length=100, description="Country name")
    country_code: Optional[str] = Field(None, min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    flag_emoji: Optional[str] = Field(None, description="Flag emoji for the country")
    is_active: Optional[bool] = Field(None, description="Whether the location is active")


# Properties shared by models stored in DB
class LocationInDBBase(LocationBase):
    """
    Base schema for locations retrieved from the database.
    """
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Properties to return to client
class Location(LocationInDBBase):
    """
    Schema for location data returned to clients.
    """
    server_count: Optional[int] = Field(0, description="Number of servers in this location")
    active_server_count: Optional[int] = Field(0, description="Number of active servers in this location")


# Properties stored in DB
class LocationInDB(LocationInDBBase):
    """
    Schema for location data stored in the database.
    """
    pass 