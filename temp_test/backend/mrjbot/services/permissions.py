from rest_framework import permissions
from .models import Service, Plan, Subscription, Config, Usage, ServiceLog, ServiceMetric, ServiceAlert
from django.utils import timezone

class IsServiceOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a service to access it.
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Service):
            return obj.owner == request.user
        elif isinstance(obj, Plan):
            return obj.service.owner == request.user
        elif isinstance(obj, Subscription):
            return obj.user == request.user
        elif isinstance(obj, Usage):
            return obj.subscription.user == request.user
        return False

class IsServiceAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to access service management features.
    """
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Service):
            return obj.owner == request.user or request.user.is_staff
        elif isinstance(obj, Plan):
            return obj.service.owner == request.user or request.user.is_staff
        elif isinstance(obj, Config):
            return obj.service.owner == request.user or request.user.is_staff
        elif isinstance(obj, ServiceLog):
            return obj.service.owner == request.user or request.user.is_staff
        elif isinstance(obj, ServiceMetric):
            return obj.service.owner == request.user or request.user.is_staff
        elif isinstance(obj, ServiceAlert):
            return obj.service.owner == request.user or request.user.is_staff
        return False

class HasValidSubscription(permissions.BasePermission):
    """
    Custom permission to only allow users with valid subscriptions to access service features.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff users can access everything
        if request.user.is_staff:
            return True
        
        # Check if user has any active subscriptions
        return Subscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        if isinstance(obj, Service):
            return Subscription.objects.filter(
                user=request.user,
                plan__service=obj,
                status='active',
                end_date__gt=timezone.now()
            ).exists()
        elif isinstance(obj, Plan):
            return Subscription.objects.filter(
                user=request.user,
                plan=obj,
                status='active',
                end_date__gt=timezone.now()
            ).exists()
        return False 