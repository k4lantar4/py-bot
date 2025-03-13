"""
API views for V2Ray management.

This module contains views for:
- Server monitoring and health checks
- Traffic usage tracking
- Server management
"""

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Max, Min
from datetime import timedelta

from main.models import Server, ServerMonitor
from v2ray.models import Inbound, Client
from .serializers import (
    ServerMonitorSerializer,
    ServerHealthSerializer,
    ServerStatsSerializer
)

class ServerMonitorViewSet(viewsets.ViewSet):
    """ViewSet for server monitoring and health checks."""
    permission_classes = [IsAuthenticated]
    
    def get_latest_monitoring(self, server_id: int) -> ServerMonitor:
        """Get latest monitoring data for a server."""
        return ServerMonitor.objects.filter(
            server_id=server_id
        ).order_by("-timestamp").first()
    
    def get_monitoring_history(self, server_id: int, hours: int = 24) -> list:
        """Get monitoring history for a server."""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return ServerMonitor.objects.filter(
            server_id=server_id,
            timestamp__gte=cutoff_time
        ).order_by("timestamp")
    
    @action(detail=True, methods=['get'])
    def health(self, request, pk=None):
        """Get server health status."""
        server = Server.objects.get(pk=pk)
        latest_data = self.get_latest_monitoring(pk)
        
        if not latest_data:
            return Response(
                {"error": "No monitoring data available"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ServerHealthSerializer(latest_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get server statistics."""
        server = Server.objects.get(pk=pk)
        history = self.get_monitoring_history(pk)
        
        if not history:
            return Response(
                {"error": "No monitoring data available"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate statistics
        stats = {
            "cpu": {
                "avg": history.aggregate(Avg("cpu_usage"))["cpu_usage__avg"],
                "max": history.aggregate(Max("cpu_usage"))["cpu_usage__max"],
                "min": history.aggregate(Min("cpu_usage"))["cpu_usage__min"]
            },
            "memory": {
                "avg": history.aggregate(Avg("memory_usage"))["memory_usage__avg"],
                "max": history.aggregate(Max("memory_usage"))["memory_usage__max"],
                "min": history.aggregate(Min("memory_usage"))["memory_usage__min"]
            },
            "disk": {
                "avg": history.aggregate(Avg("disk_usage"))["disk_usage__avg"],
                "max": history.aggregate(Max("disk_usage"))["disk_usage__max"],
                "min": history.aggregate(Min("disk_usage"))["disk_usage__min"]
            },
            "network": {
                "total_usage_gb": history.last().get_network_usage_gb(),
                "current_speed_mbps": history.last().get_network_speed_mbps()
            },
            "io": {
                "current_speed_mbps": history.last().get_io_speed_mbps()
            },
            "connections": {
                "avg": history.aggregate(Avg("active_connections"))["active_connections__avg"],
                "max": history.aggregate(Max("active_connections"))["active_connections__max"],
                "min": history.aggregate(Min("active_connections"))["active_connections__min"]
            },
            "load": {
                "1min": history.last().load_average_1min,
                "5min": history.last().load_average_5min,
                "15min": history.last().load_average_15min
            }
        }
        
        serializer = ServerStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get server monitoring history."""
        server = Server.objects.get(pk=pk)
        hours = int(request.query_params.get('hours', 24))
        
        history = self.get_monitoring_history(pk, hours)
        serializer = ServerMonitorSerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all_health(self, request):
        """Get health status for all servers."""
        servers = Server.objects.filter(is_active=True)
        data = []
        
        for server in servers:
            latest_data = self.get_latest_monitoring(server.id)
            if latest_data:
                serializer = ServerHealthSerializer(latest_data)
                data.append(serializer.data)
        
        return Response(data)
