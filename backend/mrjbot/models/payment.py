from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel
from .user import User
from .service import Subscription


class Payment(BaseModel):
    """Payment model for tracking payments."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )

    PAYMENT_METHOD_CHOICES = (
        ('wallet', _('Wallet')),
        ('card', _('Card')),
        ('crypto', _('Cryptocurrency')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_data = models.JSONField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"


class Transaction(BaseModel):
    """Transaction model for tracking wallet transactions."""
    TYPE_CHOICES = (
        ('deposit', _('Deposit')),
        ('withdrawal', _('Withdrawal')),
        ('commission', _('Commission')),
        ('refund', _('Refund')),
    )

    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount}"


class Commission(BaseModel):
    """Commission model for tracking seller commissions."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, related_name='commissions', null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Commission')
        verbose_name_plural = _('Commissions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.seller.username} - {self.amount} - {self.status}"


class WithdrawalRequest(BaseModel):
    """Withdrawal request model for seller withdrawals."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, related_name='withdrawal_requests', null=True, blank=True)
    bank_account = models.CharField(max_length=50)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Withdrawal Request')
        verbose_name_plural = _('Withdrawal Requests')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.seller.username} - {self.amount} - {self.status}" 