"""
Celery tasks for V2Ray management.

This module contains Celery tasks for:
- Server monitoring and health checks
- Traffic usage tracking
- Server synchronization
- Notification sending
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models import F
from django.db import transaction
from django.conf import settings

from main.models import Server, ServerMonitor, User
from v2ray.models import Inbound, Client, ServerMetrics, ServerHealthCheck, ServerRotationLog
from utils.xui_api import XUIClient
from utils.notifications import send_telegram_notification
from utils.server_sync import sync_server, sync_all_servers, check_server_health
from v2ray.sync_manager import ServerSyncManager

logger = logging.getLogger(__name__)

@shared_task
def sync_servers() -> None:
    """
    Synchronize all active servers.
    This task should be run every 5 minutes.
    """
    try:
        async with ServerSyncManager() as sync_manager:
            results = await sync_manager.sync_all_servers()
            
            if results['failed'] > 0:
                await send_telegram_notification(
                    f"⚠️ Server sync completed with {results['failed']} failures\n"
                    f"Total: {results['total']}, Success: {results['success']}"
                )
    except Exception as e:
        logger.error(f"Error in sync_servers task: {str(e)}")
        await send_telegram_notification(
            f"❌ Server sync failed: {str(e)}"
        )

@shared_task
def monitor_servers() -> None:
    """
    Monitor all active servers and record their status.
    This task should be run every 5 minutes.
    """
    try:
        async with ServerSyncManager() as sync_manager:
            servers = Server.objects.filter(is_active=True)
            
            for server in servers:
                try:
                    # Get server metrics
                    metrics = await sync_manager.get_server_metrics(server)
                    
                    # Record metrics
                    for metric in metrics:
                        ServerMetrics.objects.create(
                            server=server,
                            cpu_usage=metric['cpu_usage'],
                            memory_usage=metric['memory_usage'],
                            disk_usage=metric['disk_usage'],
                            network_in=metric['network_in'],
                            network_out=metric['network_out'],
                            active_connections=metric['active_connections']
                        )
                    
                    # Check for high resource usage
                    latest_metric = metrics[0] if metrics else None
                    if latest_metric:
                        if (
                            latest_metric['cpu_usage'] > 80 or
                            latest_metric['memory_usage'] > 80 or
                            latest_metric['disk_usage'] > 80
                        ):
                            await send_telegram_notification(
                                f"⚠️ High resource usage on server {server.name}\n"
                                f"CPU: {latest_metric['cpu_usage']}%\n"
                                f"Memory: {latest_metric['memory_usage']}%\n"
                                f"Disk: {latest_metric['disk_usage']}%"
                            )
                except Exception as e:
                    logger.error(f"Error monitoring server {server.name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in monitor_servers task: {str(e)}")

@shared_task
def check_server_health() -> None:
    """
    Check server health and perform automatic rotation if needed.
    This task should be run every 15 minutes.
    """
    try:
        async with ServerSyncManager() as sync_manager:
            servers = Server.objects.filter(is_active=True)
            
            for server in servers:
                try:
                    # Check server health
                    health = await sync_manager.check_server_health(server)
                    
                    # Record health check
                    ServerHealthCheck.objects.create(
                        server=server,
                        status=health['is_healthy'] and 'healthy' or 'offline',
                        cpu_usage=health['cpu_usage'],
                        memory_usage=health['memory_usage'],
                        disk_usage=health['disk_usage'],
                        uptime=health['uptime'],
                        error_message=health.get('error', '')
                    )
                    
                    # Rotate subscriptions if server is unhealthy
                    if not health['is_healthy']:
                        await sync_manager.rotate_subscriptions(server)
                        
                except Exception as e:
                    logger.error(f"Error checking health for server {server.name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in check_server_health task: {str(e)}")

@shared_task
def cleanup_old_monitoring_data() -> None:
    """
    Clean up old monitoring data to prevent database bloat.
    This task should be run daily.
    """
    try:
        # Keep only last 7 days of data
        cutoff_date = timezone.now() - timedelta(days=7)
        
        # Delete old metrics
        ServerMetrics.objects.filter(timestamp__lt=cutoff_date).delete()
        
        # Delete old health checks
        ServerHealthCheck.objects.filter(timestamp__lt=cutoff_date).delete()
        
        # Delete old rotation logs
        ServerRotationLog.objects.filter(timestamp__lt=cutoff_date).delete()
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_monitoring_data task: {str(e)}")

@shared_task
def update_seller_commissions() -> None:
    """
    Update seller commissions based on sales.
    This task should be run daily.
    """
    try:
        sellers = User.objects.filter(role__name='seller')
        
        for seller in sellers:
            try:
                # Calculate commission
                total_sales = seller.total_sales
                commission_rate = seller.commission_rate
                commission = total_sales * (commission_rate / 100)
                
                # Update seller's wallet
                seller.wallet_balance = F('wallet_balance') + commission
                seller.save()
                
                # Send notification
                if commission > 0:
                    await send_telegram_notification(
                        f"💰 Commission updated for seller {seller.username}\n"
                        f"Amount: {commission:.2f}"
                    )
            except Exception as e:
                logger.error(f"Error updating commission for seller {seller.username}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in update_seller_commissions task: {str(e)}") 