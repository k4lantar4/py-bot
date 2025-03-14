"""
Server management service for V2Ray panels.

This module handles server synchronization, health checks, and management
across multiple 3x-UI panels.
"""

import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
import asyncio
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServerStatus(Enum):
    """Server status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class ServerInfo:
    """Server information data class."""
    id: str
    name: str
    host: str
    port: int
    panel_url: str
    panel_username: str
    panel_password: str
    status: ServerStatus
    last_sync: datetime
    traffic_used: int
    traffic_total: int
    uptime: float
    load: float
    memory_used: float
    memory_total: float
    disk_used: float
    disk_total: float
    tags: List[str]
    location: str
    bandwidth_limit: int
    is_active: bool

class ServerManager:
    """Manages multiple V2Ray servers and their synchronization."""
    
    def __init__(self):
        self.servers: Dict[str, ServerInfo] = {}
        self.sync_interval = 300  # 5 minutes
        self.health_check_interval = 60  # 1 minute
        self._sync_task = None
        self._health_check_task = None
    
    async def start(self):
        """Start the server manager tasks."""
        self._sync_task = asyncio.create_task(self._sync_loop())
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def stop(self):
        """Stop the server manager tasks."""
        if self._sync_task:
            self._sync_task.cancel()
        if self._health_check_task:
            self._health_check_task.cancel()
    
    async def add_server(
        self,
        name: str,
        host: str,
        port: int,
        panel_url: str,
        panel_username: str,
        panel_password: str,
        location: str,
        bandwidth_limit: int = 0,
        tags: List[str] = None
    ) -> ServerInfo:
        """Add a new server to the manager."""
        server_id = str(uuid.uuid4())
        server = ServerInfo(
            id=server_id,
            name=name,
            host=host,
            port=port,
            panel_url=panel_url,
            panel_username=panel_username,
            panel_password=panel_password,
            status=ServerStatus.OFFLINE,
            last_sync=datetime.now(),
            traffic_used=0,
            traffic_total=0,
            uptime=0.0,
            load=0.0,
            memory_used=0.0,
            memory_total=0.0,
            disk_used=0.0,
            disk_total=0.0,
            tags=tags or [],
            location=location,
            bandwidth_limit=bandwidth_limit,
            is_active=True
        )
        self.servers[server_id] = server
        return server
    
    async def remove_server(self, server_id: str) -> bool:
        """Remove a server from the manager."""
        if server_id in self.servers:
            del self.servers[server_id]
            return True
        return False
    
    async def get_server(self, server_id: str) -> Optional[ServerInfo]:
        """Get server information by ID."""
        return self.servers.get(server_id)
    
    async def get_all_servers(self) -> List[ServerInfo]:
        """Get all servers."""
        return list(self.servers.values())
    
    async def get_active_servers(self) -> List[ServerInfo]:
        """Get all active servers."""
        return [s for s in self.servers.values() if s.is_active]
    
    async def get_servers_by_location(self, location: str) -> List[ServerInfo]:
        """Get servers by location."""
        return [s for s in self.servers.values() if s.location == location]
    
    async def get_servers_by_tag(self, tag: str) -> List[ServerInfo]:
        """Get servers by tag."""
        return [s for s in self.servers.values() if tag in s.tags]
    
    async def _sync_loop(self):
        """Main synchronization loop."""
        while True:
            try:
                await self._sync_all_servers()
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
            await asyncio.sleep(self.sync_interval)
    
    async def _health_check_loop(self):
        """Main health check loop."""
        while True:
            try:
                await self._check_all_servers()
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
            await asyncio.sleep(self.health_check_interval)
    
    async def _sync_all_servers(self):
        """Synchronize all servers with their panels."""
        for server in self.servers.values():
            try:
                await self._sync_server(server)
            except Exception as e:
                logger.error(f"Error syncing server {server.id}: {e}")
                server.status = ServerStatus.ERROR
    
    async def _check_all_servers(self):
        """Check health of all servers."""
        for server in self.servers.values():
            try:
                await self._check_server_health(server)
            except Exception as e:
                logger.error(f"Error checking server {server.id}: {e}")
                server.status = ServerStatus.ERROR
    
    async def _sync_server(self, server: ServerInfo):
        """Synchronize a single server with its panel."""
        async with aiohttp.ClientSession() as session:
            # Login to panel
            login_data = {
                "username": server.panel_username,
                "password": server.panel_password
            }
            async with session.post(f"{server.panel_url}/login", json=login_data) as response:
                if response.status != 200:
                    raise Exception("Failed to login to panel")
            
            # Get server stats
            async with session.get(f"{server.panel_url}/server/stats") as response:
                if response.status != 200:
                    raise Exception("Failed to get server stats")
                stats = await response.json()
            
            # Update server info
            server.traffic_used = stats.get("traffic_used", 0)
            server.traffic_total = stats.get("traffic_total", 0)
            server.uptime = stats.get("uptime", 0.0)
            server.load = stats.get("load", 0.0)
            server.memory_used = stats.get("memory_used", 0.0)
            server.memory_total = stats.get("memory_total", 0.0)
            server.disk_used = stats.get("disk_used", 0.0)
            server.disk_total = stats.get("disk_total", 0.0)
            server.last_sync = datetime.now()
            server.status = ServerStatus.ONLINE
    
    async def _check_server_health(self, server: ServerInfo):
        """Check health of a single server."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{server.panel_url}/health") as response:
                    if response.status != 200:
                        server.status = ServerStatus.OFFLINE
                    else:
                        health_data = await response.json()
                        if health_data.get("maintenance", False):
                            server.status = ServerStatus.MAINTENANCE
                        else:
                            server.status = ServerStatus.ONLINE
        except Exception:
            server.status = ServerStatus.OFFLINE
    
    async def get_server_stats(self, server_id: str) -> Dict:
        """Get detailed statistics for a server."""
        server = await self.get_server(server_id)
        if not server:
            return None
        
        return {
            "id": server.id,
            "name": server.name,
            "status": server.status.value,
            "location": server.location,
            "traffic": {
                "used": server.traffic_used,
                "total": server.traffic_total,
                "remaining": max(0, server.traffic_total - server.traffic_used)
            },
            "system": {
                "uptime": server.uptime,
                "load": server.load,
                "memory": {
                    "used": server.memory_used,
                    "total": server.memory_total,
                    "percentage": (server.memory_used / server.memory_total * 100) if server.memory_total > 0 else 0
                },
                "disk": {
                    "used": server.disk_used,
                    "total": server.disk_total,
                    "percentage": (server.disk_used / server.disk_total * 100) if server.disk_total > 0 else 0
                }
            },
            "last_sync": server.last_sync.isoformat(),
            "tags": server.tags,
            "bandwidth_limit": server.bandwidth_limit,
            "is_active": server.is_active
        } 