"""
Celery tasks for V2Ray management.

This module contains Celery tasks for:
- Server monitoring and health checks
- Traffic usage tracking
- Automatic server rotation
- Notification sending
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models import F
from django.db import transaction

from main.models import Server, ServerMonitor
from v2ray.models import Inbound, Client
from utils.xui_api import XUIClient
from utils.notifications import send_telegram_notification

logger = logging.getLogger(__name__)

@shared_task
def monitor_servers() -> None:
    """
    Monitor all active servers and record their status.
    This task should be run every 5 minutes.
    """
    servers = Server.objects.filter(is_active=True)
    
    for server in servers:
        try:
            # Get server status from 3x-UI
            xui_client = XUIClient(
                base_url=server.url,
                username=server.username,
                password=server.password
            )
            
            status = xui_client.get_server_status()
            
            # Record monitoring data
            ServerMonitor.objects.create(
                server=server,
                cpu_usage=status.get("cpu_usage", 0),
                memory_usage=status.get("memory_usage", 0),
                disk_usage=status.get("disk_usage", 0),
                uptime_seconds=status.get("uptime", 0),
                active_connections=status.get("active_connections", 0)
            )
            
            # Check for health issues
            if status.get("cpu_usage", 0) > 90:
                send_telegram_notification(
                    f"⚠️ High CPU usage on server {server.name}: {status['cpu_usage']}%"
                )
            
            if status.get("memory_usage", 0) > 90:
                send_telegram_notification(
                    f"⚠️ High memory usage on server {server.name}: {status['memory_usage']}%"
                )
            
            if status.get("disk_usage", 0) > 90:
                send_telegram_notification(
                    f"⚠️ High disk usage on server {server.name}: {status['disk_usage']}%"
                )
            
        except Exception as e:
            logger.error(f"Error monitoring server {server.name}: {e}")
            send_telegram_notification(
                f"❌ Error monitoring server {server.name}: {str(e)}"
            )

@shared_task
def check_server_health() -> None:
    """
    Check server health and perform automatic rotation if needed.
    This task should be run every 15 minutes.
    """
    servers = Server.objects.filter(is_active=True)
    
    for server in servers:
        try:
            # Get latest monitoring data
            latest_data = ServerMonitor.objects.filter(
                server=server
            ).order_by("-timestamp").first()
            
            if not latest_data:
                continue
            
            # Check if server is unhealthy
            is_unhealthy = (
                latest_data.cpu_usage > 95 or
                latest_data.memory_usage > 95 or
                latest_data.disk_usage > 95 or
                latest_data.active_connections > 1000  # Adjust threshold as needed
            )
            
            if is_unhealthy:
                # Find alternative server
                alternative_server = Server.objects.filter(
                    is_active=True,
                    id__ne=server.id
                ).order_by("?").first()
                
                if alternative_server:
                    # Rotate subscriptions to alternative server
                    with transaction.atomic():
                        subscriptions = server.v2ray_subscriptions.filter(
                            status="active"
                        )
                        
                        for subscription in subscriptions:
                            # Create new client on alternative server
                            xui_client = XUIClient(
                                base_url=alternative_server.url,
                                username=alternative_server.username,
                                password=alternative_server.password
                            )
                            
                            # Get inbound from alternative server
                            inbounds = xui_client.get_inbounds()
                            if not inbounds:
                                continue
                            
                            inbound = inbounds[0]  # Use first available inbound
                            
                            # Create new client
                            client = xui_client.create_client(
                                inbound_id=inbound["id"],
                                email=subscription.client_email,
                                total_gb=subscription.data_limit_gb,
                                expire_days=subscription.remaining_days()
                            )
                            
                            if client:
                                # Update subscription
                                subscription.server = alternative_server
                                subscription.inbound_id = inbound["id"]
                                subscription.save()
                                
                                # Send notification
                                send_telegram_notification(
                                    f"🔄 Subscription {subscription.id} rotated to server {alternative_server.name}"
                                )
                
                else:
                    send_telegram_notification(
                        f"⚠️ No alternative server available for rotation from {server.name}"
                    )
            
        except Exception as e:
            logger.error(f"Error checking health for server {server.name}: {e}")
            send_telegram_notification(
                f"❌ Error checking health for server {server.name}: {str(e)}"
            )

@shared_task
def cleanup_old_monitoring_data() -> None:
    """
    Clean up old monitoring data to prevent database bloat.
    This task should be run daily.
    """
    # Keep last 7 days of data
    cutoff_date = timezone.now() - timedelta(days=7)
    
    ServerMonitor.objects.filter(
        timestamp__lt=cutoff_date
    ).delete() 