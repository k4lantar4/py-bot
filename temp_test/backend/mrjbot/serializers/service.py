from rest_framework import serializers

from .base import BaseModelSerializer
from ..models import Service, Plan, Subscription


class ServiceSerializer(BaseModelSerializer):
    """Serializer for Service model."""
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'icon',
            'is_enabled', 'order', 'created_at',
            'updated_at', 'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class PlanSerializer(BaseModelSerializer):
    """Serializer for Plan model."""
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = Plan
        fields = [
            'id', 'service', 'service_name', 'name',
            'description', 'price', 'duration_days',
            'max_devices', 'is_enabled', 'order',
            'created_at', 'updated_at', 'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class SubscriptionSerializer(BaseModelSerializer):
    """Serializer for Subscription model."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    service_name = serializers.CharField(source='plan.service.name', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_username', 'plan',
            'plan_name', 'service_name', 'status',
            'start_date', 'end_date', 'credentials',
            'notes', 'created_at', 'updated_at',
            'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new subscription."""
    class Meta:
        model = Subscription
        fields = ['user', 'plan', 'notes']

    def validate(self, attrs):
        user = attrs['user']
        plan = attrs['plan']
        
        # Check if user already has an active subscription for this plan
        if Subscription.objects.filter(
            user=user,
            plan=plan,
            status='active',
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "User already has an active subscription for this plan."
            )
        
        return attrs


class SubscriptionUpdateSerializer(BaseModelSerializer):
    """Serializer for updating a subscription."""
    class Meta:
        model = Subscription
        fields = ['status', 'notes'] 