from django.contrib.auth import get_user_model
from rest_framework import serializers

from .base import BaseModelSerializer

User = get_user_model()


class UserSerializer(BaseModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'phone', 'telegram_id', 'telegram_username', 'balance',
            'company_name', 'tax_id', 'bank_account', 'address',
            'created_at', 'updated_at', 'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user."""
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'role', 'phone',
            'telegram_id', 'telegram_username', 'company_name',
            'tax_id', 'bank_account', 'address',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(BaseModelSerializer):
    """Serializer for updating a user."""
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'company_name', 'tax_id', 'bank_account', 'address',
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs 