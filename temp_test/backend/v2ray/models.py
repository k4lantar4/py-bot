"""
Models for V2Ray management system.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from main.models import Server

# Create your models here.

class Inbound(models.Model):
    """Model for V2Ray inbounds."""
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='inbounds')
    port = models.PositiveIntegerField()
    protocol = models.CharField(max_length=20)
    settings = models.JSONField()
    stream_settings = models.JSONField()
    remark = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['server', 'port']
        ordering = ['port']
    
    def __str__(self):
        return f"{self.server.name} - {self.protocol}:{self.port}"

class Client(models.Model):
    """Model for V2Ray clients."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='v2ray_clients')
    inbound = models.ForeignKey(Inbound, on_delete=models.CASCADE, related_name='clients')
    email = models.EmailField()
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    flow = models.CharField(max_length=50, blank=True)
    total_gb = models.PositiveIntegerField(default=0)
    expire_days = models.PositiveIntegerField(default=0)
    enable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['inbound', 'email']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.email}"
    
    def is_expired(self):
        if self.expire_days == 0:
            return False
        return timezone.now() > (self.created_at + timezone.timedelta(days=self.expire_days))
    
    def remaining_days(self):
        if self.expire_days == 0:
            return 0
        delta = (self.created_at + timezone.timedelta(days=self.expire_days)) - timezone.now()
        return max(0, delta.days)

class ServerMetrics(models.Model):
    """Model for server performance metrics."""
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='metrics')
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    network_in = models.BigIntegerField()
    network_out = models.BigIntegerField()
    active_connections = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['server', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.server.name} - {self.timestamp}"

class ServerHealthCheck(models.Model):
    """Model for server health check results."""
    STATUS_CHOICES = (
        ('healthy', _('Healthy')),
        ('warning', _('Warning')),
        ('critical', _('Critical')),
        ('offline', _('Offline')),
    )
    
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='health_checks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    uptime = models.PositiveIntegerField()
    error_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['server', 'timestamp']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.server.name} - {self.status} - {self.timestamp}"
    
    def calculate_status(self):
        """Calculate health status based on metrics."""
        if self.error_message:
            return 'offline'
        
        if (
            self.cpu_usage > 95 or
            self.memory_usage > 95 or
            self.disk_usage > 95
        ):
            return 'critical'
        
        if (
            self.cpu_usage > 80 or
            self.memory_usage > 80 or
            self.disk_usage > 80
        ):
            return 'warning'
        
        return 'healthy'

class ServerRotationLog(models.Model):
    """Model for server rotation logs."""
    STATUS_CHOICES = (
        ('success', _('Success')),
        ('failed', _('Failed')),
        ('skipped', _('Skipped')),
    )
    
    subscription = models.ForeignKey('main.Subscription', on_delete=models.CASCADE, related_name='rotation_logs')
    old_server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='rotated_from')
    new_server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='rotated_to')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['subscription', 'timestamp']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.subscription.id} - {self.old_server.name} -> {self.new_server.name} - {self.status}"

class SyncLog(models.Model):
    """Model for 3x-UI sync logs"""
    STATUS_CHOICES = (
        ('success', _('Success')),
        ('failed', _('Failed')),
        ('partial', _('Partial Success')),
    )
    
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='sync_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    message = models.TextField(blank=True)
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.server.name} - {self.status} - {self.created_at}"

class ClientConfig(models.Model):
    """Model for storing client configuration links"""
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='config')
    vmess_link = models.TextField(blank=True, null=True)
    vless_link = models.TextField(blank=True, null=True)
    trojan_link = models.TextField(blank=True, null=True)
    shadowsocks_link = models.TextField(blank=True, null=True)
    subscription_url = models.URLField(blank=True, null=True)
    qrcode_data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Config for {self.client.email}"
