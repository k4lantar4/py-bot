from rest_framework import serializers
from .models import Service, Plan, Subscription, Config, Usage, ServiceLog, ServiceMetric, ServiceAlert

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class UsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usage
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ServiceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLog
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ServiceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMetric
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ServiceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAlert
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at') 