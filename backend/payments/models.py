from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import secrets
import uuid

# Create your models here.

class CardOwner(models.Model):
    """Model for tracking card owners"""
    name = models.CharField(max_length=100, verbose_name=_('Owner Name'))
    card_number = models.CharField(max_length=20, unique=True, verbose_name=_('Card Number'))
    bank_name = models.CharField(max_length=50, verbose_name=_('Bank Name'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Is Verified'))
    verification_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_card_owners'
    )
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = _('Card Owner')
        verbose_name_plural = _('Card Owners')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.card_number}"
    
    def verify(self, admin_user):
        """Verify a card owner"""
        self.is_verified = True
        self.verification_date = timezone.now()
        self.verified_by = admin_user
        self.save()

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
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'payments'
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.type} - {self.status}"


class CardPayment(models.Model):
    """Model for card to card payments"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
        ('retry', _('Retry Required')),
    )
    
    VERIFICATION_METHOD_CHOICES = (
        ('manual', _('Manual Verification')),
        ('ocr', _('OCR Verification')),
        ('both', _('Both Manual & OCR')),
    )
    
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='card_payment_details')
    card_owner = models.ForeignKey(CardOwner, on_delete=models.PROTECT, related_name='payments', null=True)
    card_number = models.CharField(max_length=20)
    reference_number = models.CharField(max_length=100)
    transfer_time = models.DateTimeField()
    verification_code = models.CharField(max_length=10, unique=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_method = models.CharField(
        max_length=10,
        choices=VERIFICATION_METHOD_CHOICES,
        default='manual'
    )
    receipt_image = models.ImageField(
        upload_to='receipts/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Receipt Image')
    )
    ocr_verified = models.BooleanField(default=False, verbose_name=_('OCR Verified'))
    ocr_data = models.JSONField(null=True, blank=True, verbose_name=_('OCR Data'))
    admin_note = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_card_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0, verbose_name=_('Retry Count'))
    max_retries = models.PositiveSmallIntegerField(default=3, verbose_name=_('Max Retries'))
    last_retry_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'payments'
        verbose_name = _('Card Payment')
        verbose_name_plural = _('Card Payments')
        ordering = ['-created_at']
    
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
    
    def can_retry(self):
        """Check if payment can be retried"""
        return (
            self.status in ['rejected', 'expired', 'retry'] and
            self.retry_count < self.max_retries
        )
    
    def retry_payment(self):
        """Retry a failed payment"""
        if not self.can_retry():
            return False
        
        self.status = 'pending'
        self.retry_count += 1
        self.last_retry_at = timezone.now()
        # Reset expiry time
        timeout_minutes = getattr(settings, 'CARD_PAYMENT_VERIFICATION_TIMEOUT_MINUTES', 30)
        self.expires_at = timezone.now() + timezone.timedelta(minutes=timeout_minutes)
        self.save()
        return True
    
    def verify_with_ocr(self, ocr_data):
        """Verify payment using OCR data"""
        try:
            # Validate OCR data matches payment details
            if (
                str(self.amount) in str(ocr_data.get('amount')) and
                self.card_number[-4:] in str(ocr_data.get('card_number')) and
                self.reference_number in str(ocr_data.get('reference'))
            ):
                self.ocr_verified = True
                self.ocr_data = ocr_data
                self.save()
                return True
            return False
        except Exception as e:
            logger.error(f"OCR verification error: {str(e)}")
            return False


class ZarinpalPayment(models.Model):
    """Model for Zarinpal payments"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('verified', _('Verified')),
        ('failed', _('Failed')),
    )
    
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='zarinpal_payment_details')
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_discount_usages')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='discount_usages')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.discount.code} - {self.amount}"
