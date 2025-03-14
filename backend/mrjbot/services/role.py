from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..models.role import Role, Permission, UserRole, RoleActivityLog
from ..utils.telegram import send_admin_notification

class RoleManager:
    """Service class for managing roles and permissions"""

    @classmethod
    def create_role(cls, name: str, description: str, permissions: List[str], 
                   created_by, is_custom: bool = True, priority: int = 0,
                   max_users: Optional[int] = None, allowed_actions: List[str] = None) -> Role:
        """Create a new role with specified permissions"""
        with transaction.atomic():
            role = Role.objects.create(
                name=name,
                description=description,
                is_custom=is_custom,
                priority=priority,
                max_users=max_users,
                created_by=created_by,
                allowed_actions=allowed_actions or []
            )

            # Add permissions
            permission_objects = Permission.objects.filter(codename__in=permissions)
            role.permissions.add(*permission_objects)

            # Log creation
            cls._log_role_activity(
                None, 'MODIFIED', created_by,
                {'action': 'created', 'role_id': role.id}
            )

            # Notify admins
            send_admin_notification(
                f"🎭 New role created: {role.name}\n"
                f"Created by: {created_by.username}\n"
                f"Permissions: {', '.join(permissions)}"
            )

            return role

    @classmethod
    def assign_role(cls, user, role: Role, assigned_by, expires_at: Optional[timezone.datetime] = None,
                   metadata: Dict = None) -> UserRole:
        """Assign a role to a user"""
        with transaction.atomic():
            if role.max_users and role.users.filter(is_active=True).count() >= role.max_users:
                raise ValidationError(_('Maximum number of users reached for this role'))

            user_role = UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=assigned_by,
                expires_at=expires_at,
                metadata=metadata or {}
            )

            # Notify admins
            send_admin_notification(
                f"👤 Role assigned: {role.name}\n"
                f"User: {user.username}\n"
                f"Assigned by: {assigned_by.username}\n"
                f"Expires: {expires_at or 'Never'}"
            )

            return user_role

    @classmethod
    def remove_role(cls, user_role: UserRole, removed_by) -> None:
        """Remove a role from a user"""
        with transaction.atomic():
            user_role.is_active = False
            user_role.save()

            cls._log_role_activity(
                user_role, 'REMOVED', removed_by,
                {'action': 'removed', 'user_id': user_role.user.id}
            )

            # Notify admins
            send_admin_notification(
                f"🚫 Role removed: {user_role.role.name}\n"
                f"User: {user_role.user.username}\n"
                f"Removed by: {removed_by.username}"
            )

    @classmethod
    def modify_role_permissions(cls, role: Role, permissions: List[str], modified_by) -> Role:
        """Modify permissions for a role"""
        with transaction.atomic():
            old_permissions = set(role.permissions.values_list('codename', flat=True))
            new_permissions = set(permissions)

            # Update permissions
            role.permissions.clear()
            permission_objects = Permission.objects.filter(codename__in=permissions)
            role.permissions.add(*permission_objects)
            role.save()

            # Log changes
            cls._log_role_activity(
                None, 'MODIFIED', modified_by,
                {
                    'action': 'permissions_modified',
                    'role_id': role.id,
                    'added': list(new_permissions - old_permissions),
                    'removed': list(old_permissions - new_permissions)
                }
            )

            # Notify admins
            send_admin_notification(
                f"🔄 Role permissions modified: {role.name}\n"
                f"Modified by: {modified_by.username}\n"
                f"Added: {', '.join(new_permissions - old_permissions)}\n"
                f"Removed: {', '.join(old_permissions - new_permissions)}"
            )

            return role

    @classmethod
    def get_user_permissions(cls, user) -> set:
        """Get all permissions for a user from their active roles"""
        active_roles = UserRole.objects.filter(
            user=user,
            is_active=True
        ).select_related('role')

        permissions = set()
        for user_role in active_roles:
            permissions.update(
                user_role.role.permissions.values_list('codename', flat=True)
            )
        return permissions

    @classmethod
    def check_permission(cls, user, permission_codename: str) -> bool:
        """Check if a user has a specific permission"""
        return permission_codename in cls.get_user_permissions(user)

    @classmethod
    def get_role_members(cls, role: Role, active_only: bool = True) -> List[Dict]:
        """Get all members of a role with their assignment details"""
        query = role.users.filter(is_active=active_only).select_related('user')
        return [
            {
                'user': assignment.user,
                'assigned_at': assignment.assigned_at,
                'expires_at': assignment.expires_at,
                'assigned_by': assignment.assigned_by,
                'metadata': assignment.metadata
            }
            for assignment in query
        ]

    @classmethod
    def _log_role_activity(cls, user_role: Optional[UserRole], action: str, 
                          performed_by, details: Dict = None) -> RoleActivityLog:
        """Log role-related activity"""
        return RoleActivityLog.objects.create(
            user_role=user_role,
            action=action,
            performed_by=performed_by,
            details=details or {}
        ) 