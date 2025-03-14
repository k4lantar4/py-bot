from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

User = get_user_model()

class Permission(models.Model):
    """Model for storing individual permissions"""
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('ADMIN', 'Administrative'),
        ('USER', 'User Management'),
        ('PAYMENT', 'Payment Management'),
        ('SERVER', 'Server Management'),
        ('SUPPORT', 'Support'),
        ('CONTENT', 'Content Management'),
        ('REPORT', 'Reporting'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')

    def __str__(self):
        return f"{self.name} ({self.category})"

class Role(models.Model):
    """Model for storing user roles with custom permissions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission)
    is_custom = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    max_users = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allowed_actions = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text=_('List of specific actions allowed for this role')
    )
    
    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return self.name

    def clean(self):
        if self.max_users is not None and self.max_users < 0:
            raise ValidationError({'max_users': _('Maximum users cannot be negative')})

    def assign_to_user(self, user):
        """Assign this role to a user"""
        if self.max_users and self.users.count() >= self.max_users:
            raise ValidationError(_('Maximum number of users reached for this role'))
        UserRole.objects.create(user=user, role=self)

    def get_all_permissions(self):
        """Get all permissions including inherited ones"""
        return self.permissions.all().distinct()

class UserRole(models.Model):
    """Model for tracking user role assignments and history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = _('user role')
        verbose_name_plural = _('user roles')

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

    def clean(self):
        if self.expires_at and self.expires_at < timezone.now():
            raise ValidationError({'expires_at': _('Expiry date cannot be in the past')})

    def save(self, *args, **kwargs):
        if self.expires_at and self.expires_at < timezone.now():
            self.is_active = False
        super().save(*args, **kwargs)
        RoleActivityLog.objects.create(
            user_role=self,
            action='ASSIGNED' if self.is_active else 'EXPIRED',
            performed_by=self.assigned_by
        )

class RoleActivityLog(models.Model):
    """Model for logging role-related activities"""
    user_role = models.ForeignKey(UserRole, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=[
        ('ASSIGNED', 'Role Assigned'),
        ('REMOVED', 'Role Removed'),
        ('MODIFIED', 'Role Modified'),
        ('EXPIRED', 'Role Expired'),
    ])
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-performed_at']
        verbose_name = _('role activity log')
        verbose_name_plural = _('role activity logs')

    def __str__(self):
        return f"{self.action} - {self.user_role} by {self.performed_by}" 