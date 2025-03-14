from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
import json
from django.utils import timezone
from django.conf import settings
import secrets
from .permissions import Permission, PermissionGroup, get_role_permissions

# Create your models here.

class Role(models.Model):
    """Model for user roles and permissions."""
    ROLE_CHOICES = (
        ('admin', _('Administrator')),
        ('seller', _('Seller')),
        ('vip', _('VIP Customer')),
        ('user', _('Regular User')),
    )
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.get_name_display()
    
    def save(self, *args, **kwargs):
        if not self.permissions:
            self.permissions = get_role_permissions(self.name)
        super().save(*args, **kwargs)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has a specific permission."""
        return permission in self.permissions
    
    def has_group_permissions(self, group: PermissionGroup) -> bool:
        """Check if role has all permissions in a group."""
        group_permissions = get_role_permissions(self.name)
        return all(p in self.permissions for p in group_permissions)
    
    class Meta:
        ordering = ['name']

class User(AbstractUser):
    """Extended user model with role-based access."""
    ROLE_CHOICES = (
        ('admin', _('Administrator')),
        ('seller', _('Seller')),
        ('vip', _('VIP Customer')),
        ('user', _('Regular User')),
    )
    
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    language_code = models.CharField(max_length=10, default='fa')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField(default=0, help_text='User points balance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = secrets.token_hex(10)
        super().save(*args, **kwargs)
    
    def add_points(self, points, description=''):
        """Add points to user balance."""
        self.points += points
        self.save()
        
        # Create points transaction
        PointsTransaction.objects.create(
            user=self,
            type='earn',
            points=points,
            description=description
        )
    
    def spend_points(self, points, description=''):
        """Spend points from user balance."""
        if self.points < points:
            return False
        
        self.points -= points
        self.save()
        
        # Create points transaction
        PointsTransaction.objects.create(
            user=self,
            type='spend',
            points=points,
            description=description
        )
        return True
    
    def get_points_history(self):
        """Get user's points transaction history."""
        return PointsTransaction.objects.filter(user=self).order_by('-created_at')
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission."""
        if self.is_admin:
            return True
        if not self.role:
            return False
        return self.role.has_permission(permission)
    
    def has_group_permissions(self, group: PermissionGroup) -> bool:
        """Check if user has all permissions in a group."""
        if self.is_admin:
            return True
        if not self.role:
            return False
        return self.role.has_group_permissions(group)
    
    def can_manage_servers(self) -> bool:
        """Check if user can manage servers."""
        return self.has_permission(Permission.MANAGE_SERVERS)
    
    def can_manage_users(self) -> bool:
        """Check if user can manage users."""
        return self.has_permission(Permission.MANAGE_USERS)
    
    def can_view_stats(self) -> bool:
        """Check if user can view statistics."""
        return self.has_permission(Permission.VIEW_METRICS)
    
    def can_sell_subscriptions(self) -> bool:
        """Check if user can sell subscriptions."""
        return self.has_permission(Permission.SELL_SUBSCRIPTIONS)
    
    def get_permissions(self) -> list:
        """Get all user permissions."""
        if self.is_admin:
            return [p for group in PermissionGroup for p in get_role_permissions(group)]
        if not self.role:
            return []
        return self.role.permissions

class Server(models.Model):
    """Model for V2Ray servers with sync support."""
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    protocol = models.CharField(max_length=20, default='vmess')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    sync_id = models.CharField(max_length=50, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_synced = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.host})"
    
    def save(self, *args, **kwargs):
        if not self.sync_id:
            self.sync_id = f"server_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    def generate_remark(self, user: User) -> str:
        """Generate unique remark for user subscription."""
        return f"MoonVpn-{self.name}-{user.id}-{uuid.uuid4().hex[:4]}"

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
    HEALTH_STATUS = (
        ('healthy', _('Healthy')),
        ('warning', _('Warning')),
        ('critical', _('Critical')),
        ('offline', _('Offline')),
    )
    
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='monitoring_data')
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS, default='healthy')
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    disk_usage = models.FloatField(null=True, blank=True)
    uptime_seconds = models.PositiveIntegerField(null=True, blank=True)
    active_connections = models.PositiveIntegerField(null=True, blank=True)
    network_in = models.BigIntegerField(null=True, blank=True, help_text="Network input in bytes")
    network_out = models.BigIntegerField(null=True, blank=True, help_text="Network output in bytes")
    network_speed_in = models.FloatField(null=True, blank=True, help_text="Network input speed in bytes/s")
    network_speed_out = models.FloatField(null=True, blank=True, help_text="Network output speed in bytes/s")
    load_average_1min = models.FloatField(null=True, blank=True)
    load_average_5min = models.FloatField(null=True, blank=True)
    load_average_15min = models.FloatField(null=True, blank=True)
    swap_usage = models.FloatField(null=True, blank=True)
    io_read = models.BigIntegerField(null=True, blank=True, help_text="Disk read in bytes")
    io_write = models.BigIntegerField(null=True, blank=True, help_text="Disk write in bytes")
    io_speed_read = models.FloatField(null=True, blank=True, help_text="Disk read speed in bytes/s")
    io_speed_write = models.FloatField(null=True, blank=True, help_text="Disk write speed in bytes/s")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.server.name} - {self.health_status} - {self.timestamp}"
    
    def calculate_health_status(self) -> str:
        """Calculate server health status based on metrics."""
        if not all([self.cpu_usage, self.memory_usage, self.disk_usage]):
            return 'offline'
        
        # Check critical conditions
        if (
            self.cpu_usage > 95 or
            self.memory_usage > 95 or
            self.disk_usage > 95 or
            self.load_average_1min > 10 or
            self.active_connections > 1000
        ):
            return 'critical'
        
        # Check warning conditions
        if (
            self.cpu_usage > 80 or
            self.memory_usage > 80 or
            self.disk_usage > 80 or
            self.load_average_1min > 5 or
            self.active_connections > 500
        ):
            return 'warning'
        
        return 'healthy'
    
    def get_network_usage_gb(self) -> float:
        """Get total network usage in GB."""
        if not all([self.network_in, self.network_out]):
            return 0
        return round((self.network_in + self.network_out) / (1024 * 1024 * 1024), 2)
    
    def get_network_speed_mbps(self) -> tuple[float, float]:
        """Get network speed in Mbps."""
        if not all([self.network_speed_in, self.network_speed_out]):
            return 0, 0
        return (
            round(self.network_speed_in * 8 / (1024 * 1024), 2),
            round(self.network_speed_out * 8 / (1024 * 1024), 2)
        )
    
    def get_io_speed_mbps(self) -> tuple[float, float]:
        """Get disk I/O speed in MB/s."""
        if not all([self.io_speed_read, self.io_speed_write]):
            return 0, 0
        return (
            round(self.io_speed_read / (1024 * 1024), 2),
            round(self.io_speed_write / (1024 * 1024), 2)
        )
    
    def get_uptime_days(self) -> float:
        """Get server uptime in days."""
        if not self.uptime_seconds:
            return 0
        return round(self.uptime_seconds / (24 * 60 * 60), 2)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['server', 'timestamp']),
            models.Index(fields=['health_status']),
        ]


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

class PointsTransaction(models.Model):
    """Model for tracking points transactions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(
        max_length=20,
        choices=[
            ('earn', 'Earned'),
            ('spend', 'Spent'),
            ('system', 'System')
        ]
    )
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type} {self.points} points"

class LiveChatSession(models.Model):
    """Model for live chat support sessions"""
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('closed', _('Closed')),
        ('transferred', _('Transferred')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    subject = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    last_message_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.subject}"

class LiveChatMessage(models.Model):
    """Model for live chat messages"""
    TYPE_CHOICES = (
        ('text', _('Text')),
        ('file', _('File')),
        ('image', _('Image')),
        ('system', _('System')),
    )
    
    session = models.ForeignKey(LiveChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')
    content = models.TextField()
    file_url = models.URLField(null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.session.user.username} - {self.type} - {self.created_at}"

class LiveChatOperator(models.Model):
    """Model for live chat operators"""
    STATUS_CHOICES = (
        ('online', _('Online')),
        ('busy', _('Busy')),
        ('offline', _('Offline')),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='operator_profile')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    max_sessions = models.PositiveIntegerField(default=5)
    current_sessions = models.PositiveIntegerField(default=0)
    last_active = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"

class LiveChatRating(models.Model):
    """Model for live chat session ratings"""
    session = models.OneToOneField(LiveChatSession, on_delete=models.CASCADE, related_name='rating')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.session.user.username} - {self.rating}"

class UserUsagePattern(models.Model):
    """Model for tracking user's usage patterns."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usage_pattern')
    average_daily_usage_gb = models.FloatField(default=0)
    peak_hours = models.JSONField(default=list)  # List of hours with highest usage
    preferred_protocols = models.JSONField(default=list)  # List of preferred protocols
    last_updated = models.DateTimeField(auto_now=True)

    def update_patterns(self, usage_data):
        """Update usage patterns based on new data."""
        self.average_daily_usage_gb = usage_data.get('average_daily_usage_gb', 0)
        self.peak_hours = usage_data.get('peak_hours', [])
        self.preferred_protocols = usage_data.get('preferred_protocols', [])
        self.save()

class PlanSuggestion(models.Model):
    """Model for storing plan suggestions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plan_suggestions')
    suggested_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def accept(self):
        """Mark suggestion as accepted."""
        self.is_accepted = True
        self.accepted_at = timezone.now()
        self.save()

class PointsRedemptionRule(models.Model):
    """Model for points redemption rules."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    reward_type = models.CharField(
        max_length=20,
        choices=[
            ('discount', 'Discount Code'),
            ('days', 'Subscription Days'),
            ('other', 'Other')
        ]
    )
    reward_value = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"

class PointsRedemption(models.Model):
    """Model for points redemptions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rule = models.ForeignKey(PointsRedemptionRule, on_delete=models.CASCADE)
    points_spent = models.IntegerField()
    reward_value = models.IntegerField()
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.rule.name}"
