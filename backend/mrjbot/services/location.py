import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Avg
from celery import shared_task

from mrjbot.models import ServerLocation, LocationGroup
from mrjbot.services.telegram import send_admin_message

class LocationManager:
    def __init__(self):
        self.check_interval = 300  # 5 minutes
        self.alert_threshold = 90  # 90% load
        
    async def check_server_health(self, server: ServerLocation) -> Dict:
        """Check server health metrics"""
        async with aiohttp.ClientSession() as session:
            try:
                # Check panel availability
                start_time = datetime.now()
                async with session.get(server.panel_url) as response:
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    is_up = response.status == 200
                
                # Get server stats from panel
                stats = await self._get_server_stats(session, server)
                
                return {
                    "latency": latency,
                    "uptime": 100 if is_up else 0,
                    "bandwidth": stats.get("bandwidth_usage", 0),
                    "connections": stats.get("current_connections", 0)
                }
                
            except Exception as e:
                print(f"Error checking server {server.name}: {str(e)}")
                return {
                    "latency": 9999,
                    "uptime": 0,
                    "bandwidth": 0,
                    "connections": 0
                }
    
    async def _get_server_stats(self, session: aiohttp.ClientSession, server: ServerLocation) -> Dict:
        """Get statistics from server panel"""
        try:
            headers = {"Authorization": f"Bearer {settings.PANEL_API_KEY}"}
            async with session.get(f"{server.panel_url}/api/stats", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except:
            return {}
    
    @shared_task
    async def monitor_servers(self):
        """Monitor all server locations"""
        servers = ServerLocation.objects.filter(status__in=["active", "overloaded"])
        
        for server in servers:
            stats = await self.check_server_health(server)
            
            # Update server metrics
            server.update_metrics(
                latency=stats["latency"],
                uptime=stats["uptime"],
                bandwidth=stats["bandwidth"]
            )
            server.update_load(stats["connections"])
            
            # Alert if server is overloaded
            if server.load_percentage >= self.alert_threshold:
                await self._alert_overload(server)
    
    async def _alert_overload(self, server: ServerLocation):
        """Send alert for overloaded server"""
        message = f"⚠️ هشدار: سرور {server.name} در وضعیت بحرانی!\n\n"
        message += f"🔄 بار فعلی: {server.load_percentage:.1f}%\n"
        message += f"⚡️ تاخیر: {server.latency:.0f}ms\n"
        message += f"📊 پهنای باند: {server.bandwidth_usage:.1f}%\n"
        message += f"⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await send_admin_message(message)
    
    def get_best_server(self, country: Optional[str] = None) -> ServerLocation:
        """Get best available server based on metrics"""
        servers = ServerLocation.objects.filter(status="active")
        if country:
            servers = servers.filter(country=country)
            
        if not servers.exists():
            raise ValueError("No available servers found")
            
        # Get server with best combination of metrics
        return servers.annotate(
            score=(100 - models.F("load_percentage")) * 0.4 +  # 40% weight to load
                  (100 - models.F("latency") / 100) * 0.3 +   # 30% weight to latency
                  models.F("uptime") * 0.3                     # 30% weight to uptime
        ).order_by("-score").first()
    
    def create_server(
        self,
        country: str,
        city: str,
        capacity: int,
        ip_address: str,
        port: int,
        panel_url: str,
        panel_type: str = "3x-ui"
    ) -> ServerLocation:
        """Create a new server location"""
        # Generate smart name
        name = self._generate_server_name(country, city, capacity)
        
        server = ServerLocation.objects.create(
            name=name,
            country=country,
            city=city,
            capacity=capacity,
            ip_address=ip_address,
            port=port,
            panel_url=panel_url,
            panel_type=panel_type
        )
        
        return server
    
    def _generate_server_name(self, country: str, city: str, capacity: int) -> str:
        """Generate smart server name"""
        # Count existing servers in this location
        count = ServerLocation.objects.filter(country=country, city=city).count()
        
        return f"MoonVpn-{country}-{capacity}-{count + 1}"
    
    @shared_task
    async def balance_load(self):
        """Balance load across server groups"""
        groups = LocationGroup.objects.filter(is_active=True)
        
        for group in groups:
            try:
                # Get overloaded servers
                overloaded = [s for s in group.locations.all() if s.status == "overloaded"]
                
                if overloaded:
                    # Try to redistribute connections
                    target = group.get_next_server()
                    if target:
                        await self._migrate_connections(overloaded[0], target)
            except Exception as e:
                print(f"Error balancing group {group.name}: {str(e)}")
    
    async def _migrate_connections(self, source: ServerLocation, target: ServerLocation):
        """Migrate connections from one server to another"""
        # Implementation depends on panel API
        pass 