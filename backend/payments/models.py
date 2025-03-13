from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import secrets
import uuid

# Create your models here.

class Transaction(models.Model):
    """Base model for all transactions"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('expired', _('Expired')),
        ('refunded', _('Refunded')),
    )
    
    TYPE_CHOICES = (
        ('deposit', _('Deposit')),
        ('purchase', _('Purchase')),
        ('refund', _('Refund')),
        ('admin', _('Admin Adjustment')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.type} - {self.status}"


class CardPayment(models.Model):
    """Model for card to card payments"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    )
    
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='card_payment')
    card_number = models.CharField(max_length=20)
    reference_number = models.CharField(max_length=100)
    transfer_time = models.DateTimeField()
    verification_code = models.CharField(max_length=10, unique=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.transaction.user.username} - {self.verification_code}"
    
    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = secrets.token_hex(5)[:10]
        if not self.expires_at:
            # Set expiry time to 30 minutes from now
            timeout_minutes = getattr(settings, 'CARD_PAYMENT_VERIFICATION_TIMEOUT_MINUTES', 30)
            self.expires_at = timezone.now() + timezone.timedelta(minutes=timeout_minutes)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class ZarinpalPayment(models.Model):
    """Model for Zarinpal payments"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('verified', _('Verified')),
        ('failed', _('Failed')),
    )
    
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='zarinpal_payment')
    authority = models.CharField(max_length=100, blank=True, null=True)
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction.user.username} - {self.authority}"


class PaymentMethod(models.Model):
    """Model for payment methods"""
    TYPE_CHOICES = (
        ('card', _('Card to Card')),
        ('zarinpal', _('Zarinpal')),
        ('wallet', _('Wallet')),
    )
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    extra_data = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.name


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
    
    def calculate_discount(self, amount):
        """Calculate discount amount"""
        if self.type == 'percentage':
            return (amount * self.value) / 100
        else:  # fixed
            return min(amount, self.value)  # Don't discount more than the amount


class DiscountUsage(models.Model):
    """Model for tracking discount code usage"""
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discount_usages')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='discount_usage')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.discount.code} - {self.amount}"
