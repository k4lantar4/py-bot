from rest_framework import serializers

from .base import BaseModelSerializer
from ..models import Notification, Setting, UserSetting


class NotificationSerializer(BaseModelSerializer):
    """Serializer for Notification model."""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_username', 'title',
            'message', 'type', 'is_read', 'action_url',
            'created_at', 'updated_at', 'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new notification."""
    class Meta:
        model = Notification
        fields = ['user', 'title', 'message', 'type', 'action_url']


class SettingSerializer(BaseModelSerializer):
    """Serializer for Setting model."""
    class Meta:
        model = Setting
        fields = [
            'id', 'key', 'value', 'description',
            'is_public', 'created_at', 'updated_at',
            'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class UserSettingSerializer(BaseModelSerializer):
    """Serializer for UserSetting model."""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserSetting
        fields = [
            'id', 'user', 'user_username', 'key',
            'value', 'created_at', 'updated_at',
            'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active'] 