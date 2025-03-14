from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ...models.role import Role, Permission
from ...services.role import RoleManager

User = get_user_model()

class Command(BaseCommand):
    help = 'Manage user roles and permissions'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')

        # Create role
        create_parser = subparsers.add_parser('create', help='Create a new role')
        create_parser.add_argument('name', type=str, help='Role name')
        create_parser.add_argument('description', type=str, help='Role description')
        create_parser.add_argument('--permissions', nargs='+', help='List of permission codenames')
        create_parser.add_argument('--priority', type=int, default=0, help='Role priority')
        create_parser.add_argument('--max-users', type=int, help='Maximum number of users')
        create_parser.add_argument('--allowed-actions', nargs='+', help='List of allowed actions')

        # Assign role
        assign_parser = subparsers.add_parser('assign', help='Assign role to user')
        assign_parser.add_argument('username', type=str, help='Username')
        assign_parser.add_argument('role_name', type=str, help='Role name')
        assign_parser.add_argument('--expires', type=str, help='Expiry date (YYYY-MM-DD)')
        assign_parser.add_argument('--metadata', type=str, help='JSON metadata')

        # Remove role
        remove_parser = subparsers.add_parser('remove', help='Remove role from user')
        remove_parser.add_argument('username', type=str, help='Username')
        remove_parser.add_argument('role_name', type=str, help='Role name')

        # List roles
        list_parser = subparsers.add_parser('list', help='List roles')
        list_parser.add_argument('--user', type=str, help='Filter by username')
        list_parser.add_argument('--active-only', action='store_true', help='Show only active roles')

        # Modify permissions
        modify_parser = subparsers.add_parser('modify', help='Modify role permissions')
        modify_parser.add_argument('role_name', type=str, help='Role name')
        modify_parser.add_argument('--add', nargs='+', help='Permissions to add')
        modify_parser.add_argument('--remove', nargs='+', help='Permissions to remove')

        # List permissions
        perms_parser = subparsers.add_parser('permissions', help='List available permissions')
        perms_parser.add_argument('--category', type=str, help='Filter by category')

    def handle(self, *args, **options):
        action = options['action']
        try:
            if action == 'create':
                self._handle_create(options)
            elif action == 'assign':
                self._handle_assign(options)
            elif action == 'remove':
                self._handle_remove(options)
            elif action == 'list':
                self._handle_list(options)
            elif action == 'modify':
                self._handle_modify(options)
            elif action == 'permissions':
                self._handle_permissions(options)
            else:
                raise CommandError('Invalid action')
        except Exception as e:
            raise CommandError(str(e))

    def _handle_create(self, options):
        """Handle role creation"""
        role = RoleManager.create_role(
            name=options['name'],
            description=options['description'],
            permissions=options.get('permissions', []),
            created_by=User.objects.filter(is_superuser=True).first(),
            priority=options.get('priority', 0),
            max_users=options.get('max_users'),
            allowed_actions=options.get('allowed_actions', [])
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created role "{role.name}" with ID {role.id}'
        ))

    def _handle_assign(self, options):
        """Handle role assignment"""
        try:
            user = User.objects.get(username=options['username'])
            role = Role.objects.get(name=options['role_name'])
        except (User.DoesNotExist, Role.DoesNotExist) as e:
            raise CommandError(str(e))

        expires_at = None
        if options.get('expires'):
            try:
                expires_at = timezone.datetime.strptime(
                    options['expires'], '%Y-%m-%d'
                ).replace(tzinfo=timezone.utc)
            except ValueError:
                raise CommandError('Invalid date format. Use YYYY-MM-DD')

        metadata = {}
        if options.get('metadata'):
            try:
                import json
                metadata = json.loads(options['metadata'])
            except json.JSONDecodeError:
                raise CommandError('Invalid JSON metadata')

        user_role = RoleManager.assign_role(
            user=user,
            role=role,
            assigned_by=User.objects.filter(is_superuser=True).first(),
            expires_at=expires_at,
            metadata=metadata
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully assigned role "{role.name}" to user "{user.username}"'
        ))

    def _handle_remove(self, options):
        """Handle role removal"""
        try:
            user = User.objects.get(username=options['username'])
            role = Role.objects.get(name=options['role_name'])
            user_role = user.role_assignments.get(role=role, is_active=True)
        except (User.DoesNotExist, Role.DoesNotExist) as e:
            raise CommandError(str(e))
        except user.role_assignments.model.DoesNotExist:
            raise CommandError('User does not have this role')

        RoleManager.remove_role(
            user_role=user_role,
            removed_by=User.objects.filter(is_superuser=True).first()
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully removed role "{role.name}" from user "{user.username}"'
        ))

    def _handle_list(self, options):
        """Handle role listing"""
        if options.get('user'):
            try:
                user = User.objects.get(username=options['user'])
                roles = user.role_assignments.filter(
                    is_active=options.get('active_only', False)
                ).select_related('role')
                self.stdout.write(f'Roles for user "{user.username}":')
                for user_role in roles:
                    self.stdout.write(f'- {user_role.role.name} '
                                    f'(expires: {user_role.expires_at or "never"})')
            except User.DoesNotExist:
                raise CommandError('User not found')
        else:
            roles = Role.objects.all()
            self.stdout.write('Available roles:')
            for role in roles:
                members = role.users.filter(is_active=True).count()
                self.stdout.write(
                    f'- {role.name} (priority: {role.priority}, '
                    f'members: {members}, max: {role.max_users or "unlimited"})'
                )

    def _handle_modify(self, options):
        """Handle role permission modification"""
        try:
            role = Role.objects.get(name=options['role_name'])
        except Role.DoesNotExist:
            raise CommandError('Role not found')

        current_perms = set(role.permissions.values_list('codename', flat=True))
        if options.get('add'):
            current_perms.update(options['add'])
        if options.get('remove'):
            current_perms.difference_update(options['remove'])

        role = RoleManager.modify_role_permissions(
            role=role,
            permissions=list(current_perms),
            modified_by=User.objects.filter(is_superuser=True).first()
        )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully modified permissions for role "{role.name}"'
        ))

    def _handle_permissions(self, options):
        """Handle permission listing"""
        permissions = Permission.objects.all()
        if options.get('category'):
            permissions = permissions.filter(category=options['category'].upper())

        self.stdout.write('Available permissions:')
        for perm in permissions:
            self.stdout.write(f'- {perm.codename} ({perm.category}): {perm.description}') 