"""
Admin service for handling administrative operations.
"""

from typing import Dict, Any, Optional
from ..utils.api import api_client

class AdminService:
    """Service for handling administrative operations."""
    
    @staticmethod
    async def get_users(token: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get list of users."""
        return await api_client.request(
            "GET",
            "/admin/users",
            token=token,
            params={"page": page, "limit": limit}
        )
    
    @staticmethod
    async def get_servers(token: str) -> Dict[str, Any]:
        """Get list of servers."""
        return await api_client.request("GET", "/admin/servers", token=token)
    
    @staticmethod
    async def get_locations(token: str) -> Dict[str, Any]:
        """Get list of locations."""
        return await api_client.request("GET", "/admin/locations", token=token)
    
    @staticmethod
    async def get_system_stats(token: str) -> Dict[str, Any]:
        """Get system statistics."""
        return await api_client.request("GET", "/admin/stats", token=token)
    
    @staticmethod
    async def get_server_status(token: str, server_id: str) -> Dict[str, Any]:
        """Get status of a specific server."""
        return await api_client.request(
            "GET",
            f"/admin/servers/{server_id}/status",
            token=token
        )

# Create global service instance
admin_service = AdminService() 