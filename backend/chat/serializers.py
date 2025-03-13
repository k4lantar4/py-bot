from rest_framework import serializers
from .models import LiveChatSession, LiveChatMessage, LiveChatOperator, LiveChatRating
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class LiveChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = LiveChatMessage
        fields = [
            'id', 'session', 'sender', 'sender_name', 'type',
            'content', 'file', 'file_name', 'file_size', 'created_at'
        ]
        read_only_fields = ['sender', 'file_size']
    
    def validate_file(self, value):
        """Validate file size and type."""
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                raise serializers.ValidationError("File size cannot exceed 5MB")
            
            allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Invalid file type")
        return value
    
    def create(self, validated_data):
        if 'file' in validated_data:
            validated_data['file_size'] = validated_data['file'].size
            validated_data['file_name'] = validated_data['file'].name
        return super().create(validated_data)

class LiveChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = LiveChatSession
        fields = [
            'id', 'user', 'user_name', 'operator', 'operator_name',
            'status', 'priority', 'subject', 'created_at', 'updated_at',
            'closed_at'
        ]
        read_only_fields = ['user', 'operator', 'closed_at']

class LiveChatOperatorSerializer(serializers.ModelSerializer):
    """Serializer for chat operators."""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = LiveChatOperator
        fields = [
            'id', 'user', 'username', 'status', 'max_concurrent_sessions',
            'current_sessions', 'last_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['current_sessions', 'last_active']

class LiveChatRatingSerializer(serializers.ModelSerializer):
    """Serializer for chat ratings."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = LiveChatRating
        fields = [
            'id', 'session', 'user', 'user_name', 'operator',
            'operator_name', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['user', 'operator']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value 