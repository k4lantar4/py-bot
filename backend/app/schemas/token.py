"""
Token schemas for the 3X-UI Management System.

This module defines the schemas for authentication tokens.
"""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for token response.
    """
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Schema for token payload.
    """
    sub: Optional[int] = None
    exp: Optional[int] = None
    type: Optional[str] = None 