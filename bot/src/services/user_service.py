"""
User service for handling user-related business logic.
"""

from typing import Dict, Any, Optional
from ..utils.api import api_client

class UserService:
    """Service for handling user-related operations."""
    
    @staticmethod
    async def get_profile(token: str) -> Dict[str, Any]:
        """Get user profile information."""
        return await api_client.request("GET", "/users/me", token=token)
    
    @staticmethod
    async def login(email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and get access token."""
        return await api_client.request(
            "POST",
            "/auth/login",
            data={"email": email, "password": password}
        )
    
    @staticmethod
    async def get_services(token: str) -> Dict[str, Any]:
        """Get user's services."""
        return await api_client.request("GET", "/services", token=token)
    
    @staticmethod
    async def get_orders(token: str) -> Dict[str, Any]:
        """Get user's orders."""
        return await api_client.request("GET", "/orders", token=token)
    
    @staticmethod
    async def get_clients(token: str) -> Dict[str, Any]:
        """Get user's clients."""
        return await api_client.request("GET", "/clients", token=token)

# Create global service instance
user_service = UserService() 