"""
Server synchronization manager for V2Ray servers.

This module provides:
- Multi-server synchronization
- Configuration management
- Health monitoring
- Automatic failover
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import F

from main.models import Server, ServerMonitor, User
from v2ray.models import Inbound, Client
from utils.notifications import send_telegram_notification

logger = logging.getLogger(__name__)

class ServerSyncManager:
    """Manager class for server synchronization."""
    
    def __init__(self):
        self.session = None
        self.sync_lock = asyncio.Lock()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def sync_server(self, server: Server) -> bool:
        """
        Synchronize a single server.
        
        Args:
            server: Server instance to sync
            
        Returns:
            True if sync successful, False otherwise
        """
        async with self.sync_lock:
            try:
                # Get server status
                status = await self._get_server_status(server)
                
                # Update server status
                server.is_active = status.get('is_active', False)
                server.is_synced = True
                server.last_sync = timezone.now()
                server.save()
                
                # Sync inbounds
                await self._sync_inbounds(server)
                
                # Sync clients
                await self._sync_clients(server)
                
                # Record monitoring data
                await self._record_monitoring_data(server, status)
                
                return True
            except Exception as e:
                logger.error(f"Error syncing server {server.name}: {str(e)}")
                server.is_synced = False
                server.save()
                return False
    
    async def sync_all_servers(self) -> Dict[str, int]:
        """
        Synchronize all active servers.
        
        Returns:
            Dict with sync results
        """
        results = {
            'total': 0,
            'success': 0,
            'failed': 0
        }
        
        servers = Server.objects.filter(is_active=True)
        results['total'] = servers.count()
        
        tasks = [self.sync_server(server) for server in servers]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results_list:
            if isinstance(result, Exception):
                results['failed'] += 1
            elif result:
                results['success'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    async def _get_server_status(self, server: Server) -> Dict:
        """Get server status from API."""
        url = f"{settings.V2RAY_API_URL}/server/{server.sync_id}/status"
        async with self.session.get(url, timeout=30) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _sync_inbounds(self, server: Server) -> None:
        """Synchronize server inbounds."""
        url = f"{settings.V2RAY_API_URL}/server/{server.sync_id}/inbounds"
        async with self.session.get(url, timeout=30) as response:
            response.raise_for_status()
            inbounds_data = await response.json()
            
            for inbound_data in inbounds_data:
                await self._update_inbound(server, inbound_data)
    
    async def _update_inbound(self, server: Server, inbound_data: Dict) -> None:
        """Update or create inbound."""
        Inbound.objects.update_or_create(
            server=server,
            port=inbound_data['port'],
            defaults={
                'protocol': inbound_data['protocol'],
                'settings': inbound_data['settings'],
                'stream_settings': inbound_data['stream_settings'],
                'remark': inbound_data['remark']
            }
        )
    
    async def _sync_clients(self, server: Server) -> None:
        """Synchronize server clients."""
        url = f"{settings.V2RAY_API_URL}/server/{server.sync_id}/clients"
        async with self.session.get(url, timeout=30) as response:
            response.raise_for_status()
            clients_data = await response.json()
            
            for client_data in clients_data:
                await self._update_client(server, client_data)
    
    async def _update_client(self, server: Server, client_data: Dict) -> None:
        """Update or create client."""
        try:
            user = User.objects.get(id=client_data['user_id'])
            inbound = Inbound.objects.get(
                server=server,
                port=client_data['inbound_port']
            )
            
            Client.objects.update_or_create(
                user=user,
                inbound=inbound,
                defaults={
                    'email': client_data['email'],
                    'uuid': client_data['uuid'],
                    'flow': client_data.get('flow', ''),
                    'total_gb': client_data['total_gb'],
                    'expire_days': client_data['expire_days'],
                    'enable': client_data['enable']
                }
            )
        except (User.DoesNotExist, Inbound.DoesNotExist) as e:
            logger.error(f"Error updating client: {str(e)}")
    
    async def _record_monitoring_data(self, server: Server, status: Dict) -> None:
        """Record server monitoring data."""
        ServerMonitor.objects.create(
            server=server,
            cpu_usage=status.get('cpu_usage', 0),
            memory_usage=status.get('memory_usage', 0),
            disk_usage=status.get('disk_usage', 0),
            uptime_seconds=status.get('uptime', 0),
            active_connections=status.get('active_connections', 0),
            network_in=status.get('network_in', 0),
            network_out=status.get('network_out', 0),
            network_speed_in=status.get('network_speed_in', 0),
            network_speed_out=status.get('network_speed_out', 0),
            load_average_1min=status.get('load_average_1min', 0),
            load_average_5min=status.get('load_average_5min', 0),
            load_average_15min=status.get('load_average_15min', 0),
            swap_usage=status.get('swap_usage', 0),
            io_read=status.get('io_read', 0),
            io_write=status.get('io_write', 0),
            io_speed_read=status.get('io_speed_read', 0),
            io_speed_write=status.get('io_speed_write', 0)
        )
    
    async def check_server_health(self, server: Server) -> Dict:
        """Check server health status."""
        try:
            status = await self._get_server_status(server)
            return {
                'is_healthy': status.get('is_active', False),
                'cpu_usage': status.get('cpu_usage', 0),
                'memory_usage': status.get('memory_usage', 0),
                'disk_usage': status.get('disk_usage', 0),
                'uptime': status.get('uptime', 0),
                'last_check': timezone.now()
            }
        except Exception as e:
            logger.error(f"Error checking server health: {str(e)}")
            return {
                'is_healthy': False,
                'error': str(e),
                'last_check': timezone.now()
            }
    
    async def get_server_metrics(self, server: Server, hours: int = 24) -> List[Dict]:
        """Get server metrics history."""
        try:
            url = f"{settings.V2RAY_API_URL}/server/{server.sync_id}/metrics"
            params = {'hours': hours}
            async with self.session.get(url, params=params, timeout=30) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error getting server metrics: {str(e)}")
            return []
    
    async def rotate_subscriptions(self, server: Server) -> None:
        """Rotate subscriptions to alternative server."""
        try:
            # Find alternative server
            alternative_server = Server.objects.filter(
                is_active=True,
                id__ne=server.id
            ).order_by("?").first()
            
            if not alternative_server:
                logger.warning(f"No alternative server available for rotation from {server.name}")
                return
            
            # Get unhealthy subscriptions
            subscriptions = server.v2ray_subscriptions.filter(
                status="active"
            )
            
            for subscription in subscriptions:
                await self._rotate_subscription(subscription, alternative_server)
                
        except Exception as e:
            logger.error(f"Error rotating subscriptions: {str(e)}")
    
    async def _rotate_subscription(self, subscription: 'Subscription', new_server: Server) -> None:
        """Rotate a single subscription to a new server."""
        try:
            # Create new client on alternative server
            client_data = {
                'email': subscription.client_email,
                'total_gb': subscription.data_limit_gb,
                'expire_days': subscription.remaining_days()
            }
            
            url = f"{settings.V2RAY_API_URL}/server/{new_server.sync_id}/clients"
            async with self.session.post(url, json=client_data, timeout=30) as response:
                response.raise_for_status()
                new_client = await response.json()
                
                # Update subscription
                subscription.server = new_server
                subscription.inbound_id = new_client['inbound_id']
                subscription.save()
                
                # Send notification
                await send_telegram_notification(
                    f"🔄 Subscription {subscription.id} rotated to server {new_server.name}"
                )
                
        except Exception as e:
            logger.error(f"Error rotating subscription {subscription.id}: {str(e)}") 