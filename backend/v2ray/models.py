from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from main.models import Server

# Create your models here.

class Inbound(models.Model):
    """Model for 3x-UI inbounds"""
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='inbounds')
    inbound_id = models.PositiveIntegerField(help_text="ID of the inbound in 3x-UI")
    protocol = models.CharField(max_length=50)
    tag = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    network = models.CharField(max_length=50)
    enable = models.BooleanField(default=True)
    expiry_time = models.DateTimeField(null=True, blank=True)
    listen = models.CharField(max_length=255, blank=True, null=True)
    total = models.BigIntegerField(default=0, help_text="Total traffic limit in bytes (0 means unlimited)")
    remark = models.CharField(max_length=255, blank=True, null=True)
    up = models.BigIntegerField(default=0, help_text="Upload traffic in bytes")
    down = models.BigIntegerField(default=0, help_text="Download traffic in bytes")
    settings = models.JSONField(null=True, blank=True)
    stream_settings = models.JSONField(null=True, blank=True)
    sniffing = models.JSONField(null=True, blank=True)
    last_sync = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.server.name} - {self.tag} ({self.protocol})"
    
    def get_total_traffic(self):
        """Get total traffic in bytes"""
        return self.up + self.down
    
    def get_total_traffic_gb(self):
        """Get total traffic in GB"""
        return round(self.get_total_traffic() / (1024 * 1024 * 1024), 2)
    
    def is_expired(self):
        """Check if the inbound is expired"""
        if not self.expiry_time:
            return False
        return timezone.now() > self.expiry_time


class Client(models.Model):
    """Model for 3x-UI clients"""
    inbound = models.ForeignKey(Inbound, on_delete=models.CASCADE, related_name='clients')
    client_id = models.CharField(max_length=255, help_text="ID of the client in 3x-UI")
    email = models.EmailField()
    enable = models.BooleanField(default=True)
    expiry_time = models.DateTimeField(null=True, blank=True)
    total = models.BigIntegerField(default=0, help_text="Total traffic limit in bytes (0 means unlimited)")
    up = models.BigIntegerField(default=0, help_text="Upload traffic in bytes")
    down = models.BigIntegerField(default=0, help_text="Download traffic in bytes")
    settings = models.JSONField(null=True, blank=True)
    subscription_id = models.CharField(max_length=255, blank=True, null=True)
    last_sync = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.email} ({self.inbound.protocol})"
    
    def get_total_traffic(self):
        """Get total traffic in bytes"""
        return self.up + self.down
    
    def get_total_traffic_gb(self):
        """Get total traffic in GB"""
        return round(self.get_total_traffic() / (1024 * 1024 * 1024), 2)
    
    def is_expired(self):
        """Check if the client is expired"""
        if not self.expiry_time:
            return False
        return timezone.now() > self.expiry_time
    
    def get_remaining_traffic_gb(self):
        """Get remaining traffic in GB"""
        if self.total == 0:  # Unlimited
            return float('inf')
        remaining = self.total - self.get_total_traffic()
        return max(0, round(remaining / (1024 * 1024 * 1024), 2))
    
    def get_traffic_usage_percentage(self):
        """Get traffic usage percentage"""
        if self.total == 0:  # Unlimited
            return 0
        return min(100, round((self.get_total_traffic() / self.total) * 100, 2))


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
