from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user.is_staff:
            return True
            
        # Check if the object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # Check if the object is the user itself
        return obj == request.user

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class IsSellerUser(permissions.BasePermission):
    """
    Custom permission to only allow seller users to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'seller')

class IsCustomerUser(permissions.BasePermission):
    """
    Custom permission to only allow customer users to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'customer')

class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow verified users to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active)

class HasValidSubscription(permissions.BasePermission):
    """
    Custom permission to only allow users with valid subscriptions to access the view.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_valid_subscription()

class IsSubscriptionOwner(permissions.BasePermission):
    """
    Custom permission to only allow subscription owners to access the view.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CanManageUsers(permissions.BasePermission):
    """
    Custom permission to only allow users with user management permissions.
    """
    def has_permission(self, request, view):
        return request.user.has_perm('users.manage_users')

class CanManageRoles(permissions.BasePermission):
    """
    Custom permission to only allow users with role management permissions.
    """
    def has_permission(self, request, view):
        return request.user.has_perm('users.manage_roles')

class CanManagePermissions(permissions.BasePermission):
    """
    Custom permission to only allow users with permission management permissions.
    """
    def has_permission(self, request, view):
        return request.user.has_perm('users.manage_permissions') 