"""
Role schemas for the 3X-UI Management System.

This module defines the schemas for role data validation and serialization.
"""

from typing import Optional

from pydantic import BaseModel


# Shared properties
class RoleBase(BaseModel):
    """Base Role schema with common fields."""
    name: Optional[str] = None
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    name: str


class RoleUpdate(RoleBase):
    """Schema for updating a role."""
    pass


class RoleInDBBase(RoleBase):
    """Schema for role retrieved from database."""
    id: int

    class Config:
        orm_mode = True


# Additional properties to return via API
class Role(RoleInDBBase):
    """Schema for role data returned via API."""
    pass 