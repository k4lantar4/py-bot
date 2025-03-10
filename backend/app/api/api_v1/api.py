"""
API router for the 3X-UI Management System.

This module defines the API router for the application.
"""

from fastapi import APIRouter

from ...api.api_v1.endpoints import auth, users

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"]) 