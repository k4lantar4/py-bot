from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.translation import gettext_lazy as _

from ..models import Notification, Setting, UserSetting
from ..serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    SettingSerializer,
    UserSettingSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get notifications based on user role."""
        if self.request.user.is_staff:
            return Notification.objects.all()
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Create a new notification."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'detail': _('All notifications marked as read.')})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)


class SettingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing settings."""
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        """Get settings based on user role."""
        if self.request.user.is_staff:
            return Setting.objects.all()
        return Setting.objects.filter(is_public=True)


class UserSettingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user settings."""
    serializer_class = UserSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get user settings."""
        return UserSetting.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new user setting."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def get_value(self, request):
        """Get a specific user setting value."""
        key = request.query_params.get('key')
        if not key:
            return Response({
                'error': _('Key parameter is required.')
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            setting = self.get_queryset().get(key=key)
            return Response({'value': setting.value})
        except UserSetting.DoesNotExist:
            return Response({
                'error': _('Setting not found.')
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def set_value(self, request):
        """Set a specific user setting value."""
        key = request.data.get('key')
        value = request.data.get('value')

        if not key or value is None:
            return Response({
                'error': _('Key and value are required.')
            }, status=status.HTTP_400_BAD_REQUEST)

        setting, created = self.get_queryset().update_or_create(
            key=key,
            defaults={'value': value}
        )
        return Response(UserSettingSerializer(setting).data) 