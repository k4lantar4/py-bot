"""
Serializers for V2Ray management.

This module contains serializers for:
- Server monitoring data
- Health status
- Statistics
"""

from rest_framework import serializers
from main.models import ServerMonitor

class ServerMonitorSerializer(serializers.ModelSerializer):
    """Serializer for server monitoring data."""
    network_usage_gb = serializers.SerializerMethodField()
    network_speed_mbps = serializers.SerializerMethodField()
    io_speed_mbps = serializers.SerializerMethodField()
    uptime_days = serializers.SerializerMethodField()
    
    class Meta:
        model = ServerMonitor
        fields = [
            'id', 'server', 'health_status', 'cpu_usage', 'memory_usage',
            'disk_usage', 'uptime_seconds', 'active_connections',
            'network_in', 'network_out', 'network_speed_in', 'network_speed_out',
            'load_average_1min', 'load_average_5min', 'load_average_15min',
            'swap_usage', 'io_read', 'io_write', 'io_speed_read', 'io_speed_write',
            'timestamp', 'network_usage_gb', 'network_speed_mbps',
            'io_speed_mbps', 'uptime_days'
        ]
        read_only_fields = fields
    
    def get_network_usage_gb(self, obj):
        return obj.get_network_usage_gb()
    
    def get_network_speed_mbps(self, obj):
        return obj.get_network_speed_mbps()
    
    def get_io_speed_mbps(self, obj):
        return obj.get_io_speed_mbps()
    
    def get_uptime_days(self, obj):
        return obj.get_uptime_days()

class ServerHealthSerializer(serializers.ModelSerializer):
    """Serializer for server health status."""
    network_usage_gb = serializers.SerializerMethodField()
    network_speed_mbps = serializers.SerializerMethodField()
    io_speed_mbps = serializers.SerializerMethodField()
    uptime_days = serializers.SerializerMethodField()
    
    class Meta:
        model = ServerMonitor
        fields = [
            'id', 'server', 'health_status', 'cpu_usage', 'memory_usage',
            'disk_usage', 'uptime_seconds', 'active_connections',
            'network_usage_gb', 'network_speed_mbps', 'io_speed_mbps',
            'uptime_days', 'timestamp'
        ]
        read_only_fields = fields
    
    def get_network_usage_gb(self, obj):
        return obj.get_network_usage_gb()
    
    def get_network_speed_mbps(self, obj):
        return obj.get_network_speed_mbps()
    
    def get_io_speed_mbps(self, obj):
        return obj.get_io_speed_mbps()
    
    def get_uptime_days(self, obj):
        return obj.get_uptime_days()

class ServerStatsSerializer(serializers.Serializer):
    """Serializer for server statistics."""
    cpu = serializers.DictField()
    memory = serializers.DictField()
    disk = serializers.DictField()
    network = serializers.DictField()
    io = serializers.DictField()
    connections = serializers.DictField()
    load = serializers.DictField() 