from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel
from .user import User


class Notification(BaseModel):
    """Notification model for user notifications."""
    TYPE_CHOICES = (
        ('info', _('Information')),
        ('success', _('Success')),
        ('warning', _('Warning')),
        ('error', _('Error')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save()


class Setting(BaseModel):
    """Setting model for system settings."""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Settings')
        ordering = ['key']

    def __str__(self):
        return self.key


class UserSetting(BaseModel):
    """User setting model for user-specific settings."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='settings')
    key = models.CharField(max_length=100)
    value = models.JSONField()

    class Meta:
        verbose_name = _('User Setting')
        verbose_name_plural = _('User Settings')
        unique_together = ('user', 'key')
        ordering = ['key']

    def __str__(self):
        return f"{self.user.username} - {self.key}" 