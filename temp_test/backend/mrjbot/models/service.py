from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel
from .user import User


class Service(BaseModel):
    """Service model for different types of services (e.g., VPN, Apple ID, etc.)."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text=_('Font Awesome icon class'))
    is_enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        ordering = ['order']

    def __str__(self):
        return self.name


class Plan(BaseModel):
    """Plan model for different service plans."""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    max_devices = models.PositiveIntegerField(default=1)
    is_enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Plan')
        verbose_name_plural = _('Plans')
        ordering = ['order']

    def __str__(self):
        return f"{self.service.name} - {self.name}"


class Subscription(BaseModel):
    """Subscription model for user subscriptions to plans."""
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('cancelled', _('Cancelled')),
        ('pending', _('Pending')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    credentials = models.JSONField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}" 