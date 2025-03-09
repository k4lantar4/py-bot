"""
API router for the 3X-UI Management System.

This module defines the API router for the application.
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, servers, locations, services, orders, discounts, messages, stats

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(servers.router, prefix="/servers", tags=["Servers"])
api_router.include_router(locations.router, prefix="/locations", tags=["Locations"])
api_router.include_router(services.router, prefix="/services", tags=["Services"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(discounts.router, prefix="/discounts", tags=["Discounts"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(stats.router, prefix="/stats", tags=["Statistics"]) 