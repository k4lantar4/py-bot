from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
import json
from django.utils import timezone
from django.conf import settings
import secrets

# Create your models here.

class User(AbstractUser):
    """Extended user model for the application"""
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    language_code = models.CharField(max_length=10, default='fa')
    is_admin = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username


class Server(models.Model):
    """Model for 3x-UI servers"""
    name = models.CharField(max_length=100)
    url = models.URLField(help_text="URL of the 3x-UI panel")
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    session_cookie = models.TextField(null=True, blank=True)
    session_expiry = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def is_session_valid(self):
        """Check if the session is still valid"""
        if not self.session_cookie or not self.session_expiry:
            return False
        return timezone.now() < self.session_expiry


class SubscriptionPlan(models.Model):
    """Model for subscription plans"""
    TYPE_CHOICES = (
        ('data', _('Data Based')),
        ('time', _('Time Based')),
        ('both', _('Data & Time Based')),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='both')
    data_limit_gb = models.PositiveIntegerField(default=0, help_text="Data limit in GB (0 means unlimited)")
    duration_days = models.PositiveIntegerField(default=30, help_text="Duration in days")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Model for user subscriptions"""
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('suspended', _('Suspended')),
        ('cancelled', _('Cancelled')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='v2ray_subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    # Store the inbound ID and client email from 3x-UI
    inbound_id = models.PositiveIntegerField(null=True, blank=True)
    client_email = models.EmailField(null=True, blank=True)
    # Store the full client config as JSON
    client_config = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    data_usage_gb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_limit_gb = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    def is_expired(self):
        return timezone.now() > self.end_date
    
    def remaining_days(self):
        if self.is_expired():
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
    
    def data_usage_percentage(self):
        if self.data_limit_gb == 0:  # Unlimited
            return 0
        return min(100, (self.data_usage_gb / self.data_limit_gb) * 100)


class Payment(models.Model):
    """Model for payments"""
    PAYMENT_TYPES = (
        ('card', _('Card to Card')),
        ('zarinpal', _('Zarinpal')),
        ('wallet', _('Wallet')),
        ('admin', _('Admin')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('expired', _('Expired')),
        ('refunded', _('Refunded')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='v2ray_payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_data = models.JSONField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.type}"


class CardPayment(models.Model):
    """Model for card to card payments"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    )
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='card_payment')
    card_number = models.CharField(max_length=20)
    reference_number = models.CharField(max_length=100)
    transfer_time = models.DateTimeField()
    verification_code = models.CharField(max_length=10, unique=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='v2ray_verified_payments')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.payment.user.username} - {self.verification_code}"
    
    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = secrets.token_hex(5)[:10]
        super().save(*args, **kwargs)


class ZarinpalPayment(models.Model):
    """Model for Zarinpal payments"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('verified', _('Verified')),
        ('failed', _('Failed')),
    )
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='zarinpal_payment')
    authority = models.CharField(max_length=100, blank=True, null=True)
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"{self.payment.user.username} - {self.authority}"


class Discount(models.Model):
    """Model for discount codes"""
    TYPE_CHOICES = (
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    )
    
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percentage')
    value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=0, help_text="0 means unlimited")
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        if not self.is_active:
            return False
        
        now = timezone.now()
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.max_uses > 0 and self.times_used >= self.max_uses:
            return False
        
        return True


class TelegramMessage(models.Model):
    """Model for storing Telegram message templates"""
    name = models.CharField(max_length=100)
    content = models.TextField()
    language_code = models.CharField(max_length=10, default='fa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.language_code})"


class ServerMonitor(models.Model):
    """Model for server monitoring data"""
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='monitoring_data')
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    disk_usage = models.FloatField(null=True, blank=True)
    uptime_seconds = models.PositiveIntegerField(null=True, blank=True)
    active_connections = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.server.name} - {self.timestamp}"


class APIKey(models.Model):
    """Model for API keys used for external services"""
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        if not self.is_active:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        return True
