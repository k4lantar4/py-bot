from rest_framework import serializers
from django.contrib.auth import get_user_model

from ..models.chat import (
    ChatSession, ChatMessage, ChatAgent,
    ChatTransfer, ChatQueueEntry
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data in chat"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class ChatAgentSerializer(serializers.ModelSerializer):
    """Serializer for chat agents"""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(write_only=True)

    class Meta:
        model = ChatAgent
        fields = [
            'id', 'user', 'username', 'is_online', 'is_available',
            'max_concurrent_chats', 'languages', 'specialties',
            'current_chats', 'total_chats_handled', 'average_rating'
        ]
        read_only_fields = [
            'is_online', 'current_chats', 'total_chats_handled',
            'average_rating'
        ]

    def create(self, validated_data):
        username = validated_data.pop('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'username': 'User does not exist'}
            )

        if ChatAgent.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                {'username': 'User is already an agent'}
            )

        validated_data['user'] = user
        return super().create(validated_data)


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    sender = UserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'session', 'sender', 'content', 'message_type',
            'file_url', 'file_name', 'file_size', 'is_read',
            'metadata', 'sent_at'
        ]
        read_only_fields = ['session', 'sender', 'sent_at']


class ChatTransferSerializer(serializers.ModelSerializer):
    """Serializer for chat transfers"""
    from_agent = ChatAgentSerializer(read_only=True)
    to_agent = serializers.PrimaryKeyRelatedField(
        queryset=ChatAgent.objects.all()
    )

    class Meta:
        model = ChatTransfer
        fields = [
            'id', 'session', 'from_agent', 'to_agent',
            'reason', 'status', 'created_at'
        ]
        read_only_fields = ['session', 'from_agent', 'status', 'created_at']


class ChatQueueEntrySerializer(serializers.ModelSerializer):
    """Serializer for chat queue entries"""
    class Meta:
        model = ChatQueueEntry
        fields = [
            'id', 'session', 'priority', 'required_language',
            'required_specialties', 'entry_time', 'last_attempt'
        ]
        read_only_fields = ['entry_time', 'last_attempt']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions"""
    user = UserSerializer(read_only=True)
    agent = ChatAgentSerializer(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    queue_entry = ChatQueueEntrySerializer(read_only=True)
    transfers = ChatTransferSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'agent', 'subject', 'category',
            'language', 'priority', 'status', 'user_data',
            'started_at', 'ended_at', 'last_message_at',
            'rating', 'feedback', 'tags', 'messages',
            'queue_entry', 'transfers'
        ]
        read_only_fields = [
            'user', 'agent', 'status', 'started_at', 'ended_at',
            'last_message_at', 'rating', 'feedback'
        ] 