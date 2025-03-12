"""
3x-UI API integration for the V2Ray Telegram bot.

This module provides functions for interacting with the 3x-UI panel API to manage V2Ray accounts.
API Documentation: https://www.postman.com/hsanaei/3x-ui/documentation/q1l5l0u/3x-ui
"""

import logging
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class XUIClient:
    """Client for interacting with 3x-UI API."""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize the XUI client.
        
        Args:
            base_url: Base URL of the 3x-UI panel
            username: Admin username
            password: Admin password
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._login()
    
    def _login(self) -> None:
        """Login to the 3x-UI panel."""
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json={
                    "username": self.username,
                    "password": self.password
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Login failed: {response.text}")
                
            logger.info("Successfully logged in to 3x-UI panel")
            
        except Exception as e:
            logger.error(f"Error logging in to 3x-UI panel: {e}")
            raise
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            API response data
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 401:
                # Session expired, try to login again
                self._login()
                response = self.session.request(method, url, **kwargs)
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise
    
    def get_inbounds(self) -> List[Dict[str, Any]]:
        """Get all inbound configurations."""
        response = self._request("GET", "/panel/api/inbounds/list")
        return response.get("obj", [])
    
    def get_inbound(self, inbound_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific inbound configuration.
        
        Args:
            inbound_id: Inbound ID
            
        Returns:
            Inbound configuration if found, None otherwise
        """
        inbounds = self.get_inbounds()
        for inbound in inbounds:
            if inbound.get("id") == inbound_id:
                return inbound
        return None
    
    def create_client(
        self,
        inbound_id: int,
        email: str,
        uuid: Optional[str] = None,
        enable: bool = True,
        flow: str = "",
        total_gb: int = 0,
        expire_days: int = 0,
        telegram_id: Optional[str] = None,
        subscription_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new client in an inbound.
        
        Args:
            inbound_id: Inbound ID
            email: Client email (identifier)
            uuid: Optional UUID (auto-generated if not provided)
            enable: Whether the client is enabled
            flow: Flow setting (e.g., "xtls-rprx-vision")
            total_gb: Total traffic limit in GB (0 for unlimited)
            expire_days: Number of days until expiry (0 for no expiry)
            telegram_id: Optional Telegram user ID
            subscription_url: Optional subscription URL
            
        Returns:
            Created client configuration
        """
        data = {
            "id": inbound_id,
            "settings": {
                "clients": [
                    {
                        "email": email,
                        "enable": enable,
                        "flow": flow,
                        "limitIp": 0,
                        "totalGB": total_gb,
                        "expiryTime": int((datetime.now() + timedelta(days=expire_days)).timestamp()) if expire_days > 0 else 0,
                        "tgId": telegram_id or "",
                        "subId": subscription_url or ""
                    }
                ]
            }
        }
        
        if uuid:
            data["settings"]["clients"][0]["id"] = uuid
        
        response = self._request("POST", f"/panel/api/inbounds/{inbound_id}/addClient", json=data)
        return response.get("obj", {})
    
    def update_client(
        self,
        inbound_id: int,
        email: str,
        enable: Optional[bool] = None,
        total_gb: Optional[int] = None,
        expire_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing client.
        
        Args:
            inbound_id: Inbound ID
            email: Client email (identifier)
            enable: Whether the client is enabled
            total_gb: New traffic limit in GB
            expire_days: New expiry days from now
            
        Returns:
            Updated client configuration
        """
        # Get current client settings
        inbound = self.get_inbound(inbound_id)
        if not inbound:
            raise Exception(f"Inbound {inbound_id} not found")
        
        settings = json.loads(inbound.get("settings", "{}"))
        clients = settings.get("clients", [])
        
        client = None
        for c in clients:
            if c.get("email") == email:
                client = c
                break
        
        if not client:
            raise Exception(f"Client {email} not found in inbound {inbound_id}")
        
        # Update client settings
        if enable is not None:
            client["enable"] = enable
        
        if total_gb is not None:
            client["totalGB"] = total_gb
        
        if expire_days is not None:
            client["expiryTime"] = int((datetime.now() + timedelta(days=expire_days)).timestamp())
        
        data = {
            "id": inbound_id,
            "settings": {
                "clients": [client]
            }
        }
        
        response = self._request("POST", f"/panel/api/inbounds/{inbound_id}/updateClient/{email}", json=data)
        return response.get("obj", {})
    
    def delete_client(self, inbound_id: int, email: str) -> bool:
        """
        Delete a client.
        
        Args:
            inbound_id: Inbound ID
            email: Client email (identifier)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._request("POST", f"/panel/api/inbounds/{inbound_id}/delClient/{email}")
            return True
        except:
            return False
    
    def get_client_traffic(self, email: str) -> Dict[str, Any]:
        """
        Get client traffic statistics.
        
        Args:
            email: Client email (identifier)
            
        Returns:
            Traffic statistics
        """
        response = self._request("GET", f"/panel/api/inbounds/getClientTraffics/{email}")
        return response.get("obj", {})
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status information."""
        response = self._request("GET", "/panel/api/status")
        return response.get("obj", {}) 