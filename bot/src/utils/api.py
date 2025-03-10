"""
API client utilities for interacting with the backend.
"""

import logging
from typing import Dict, Any, Optional
import httpx
from ..config.settings import settings

logger = logging.getLogger(__name__)

class APIClient:
    """Client for making API requests to the backend."""
    
    def __init__(self):
        """Initialize the API client."""
        self.client = httpx.AsyncClient(timeout=settings.API_TIMEOUT)
    
    async def request(
        self,
        method: str,
        endpoint: str,
        token: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            token: JWT token for authentication
            data: Request data
            params: Query parameters
            
        Returns:
            API response as dictionary
        """
        url = f"{settings.API_BASE_URL}{endpoint}"
        headers = {}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = await self.client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await self.client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = await self.client.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await self.client.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"API request error: {e.response.status_code} - {e.response.text}")
            try:
                return e.response.json()
            except:
                return {"detail": f"Error: {e}"}
        except Exception as e:
            logger.error(f"API request exception: {e}")
            return {"detail": f"Error: {e}"}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Create global API client instance
api_client = APIClient() 