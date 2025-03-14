from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """Base serializer for all model serializers."""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True) 