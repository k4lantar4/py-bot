from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel


class User(AbstractUser, BaseModel):
    """Custom user model."""
    ROLE_CHOICES = (
        ('admin', _('Admin')),
        ('seller', _('Seller')),
        ('customer', _('Customer')),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telegram_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    telegram_username = models.CharField(max_length=50, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    tax_id = models.CharField(max_length=50, null=True, blank=True)
    bank_account = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_seller(self):
        return self.role == 'seller'

    @property
    def is_customer(self):
        return self.role == 'customer' 