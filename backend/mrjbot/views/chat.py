from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from ..models.chat import ChatSession, ChatAgent, ChatMessage
from ..services.chat import ChatManager
from ..serializers.chat import (
    ChatSessionSerializer, ChatMessageSerializer,
    ChatAgentSerializer, ChatTransferSerializer
)


class ChatViewSet(viewsets.ModelViewSet):
    """ViewSet for chat operations"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        """Get chat sessions for current user"""
        user = self.request.user
        if ChatAgent.objects.filter(user=user).exists():
            # Agents can see all chats assigned to them
            return ChatSession.objects.filter(
                Q(agent__user=user) |
                Q(status='WAITING')
            ).order_by('-started_at')
        else:
            # Regular users can only see their own chats
            return ChatSession.objects.filter(
                user=user
            ).order_by('-started_at')

    def perform_create(self, serializer):
        """Create a new chat session"""
        ChatManager.start_chat(
            user=self.request.user,
            subject=serializer.validated_data['subject'],
            category=serializer.validated_data['category'],
            language=serializer.validated_data.get('language', 'fa'),
            priority=serializer.validated_data.get('priority', 2),
            specialties=serializer.validated_data.get('specialties'),
            user_data=serializer.validated_data.get('user_data')
        )

    @action(detail=True, methods=['post'])
    def messages(self, request, pk=None):
        """Get chat messages"""
        session = self.get_object()
        limit = request.data.get('limit', 50)
        before = request.data.get('before')

        messages = ChatManager.get_chat_messages(
            session=session,
            limit=limit,
            before=before
        )

        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in the chat"""
        session = self.get_object()
        content = request.data.get('content')
        message_type = request.data.get('type', 'TEXT')
        file_url = request.data.get('file_url')
        file_name = request.data.get('file_name')
        file_size = request.data.get('file_size')
        metadata = request.data.get('metadata')

        message = ChatManager.send_message(
            session=session,
            sender=request.user,
            content=content,
            message_type=message_type,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            metadata=metadata
        )

        serializer = ChatMessageSerializer(message)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close the chat session"""
        session = self.get_object()
        rating = request.data.get('rating')
        feedback = request.data.get('feedback')

        ChatManager.close_chat(
            session=session,
            rating=rating,
            feedback=feedback
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer chat to another agent"""
        session = self.get_object()
        serializer = ChatTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if user is an agent
        try:
            from_agent = ChatAgent.objects.get(user=request.user)
        except ChatAgent.DoesNotExist:
            return Response(
                {'error': _('Only agents can transfer chats')},
                status=status.HTTP_403_FORBIDDEN
            )

        transfer = ChatManager.transfer_chat(
            session=session,
            from_agent=from_agent,
            to_agent=serializer.validated_data['to_agent'],
            reason=serializer.validated_data['reason']
        )

        return Response(serializer.data)


class ChatAgentViewSet(viewsets.ModelViewSet):
    """ViewSet for chat agent operations"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChatAgentSerializer
    queryset = ChatAgent.objects.all()

    def get_queryset(self):
        """Get chat agents"""
        # Only show online agents by default
        if self.action == 'list':
            return self.queryset.filter(is_online=True)
        return self.queryset

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update agent's online/available status"""
        agent = self.get_object()

        # Only allow updating own status
        if agent.user != request.user:
            return Response(
                {'error': _('Cannot update other agent\'s status')},
                status=status.HTTP_403_FORBIDDEN
            )

        is_online = request.data.get('is_online')
        is_available = request.data.get('is_available')

        ChatManager.update_agent_status(
            agent=agent,
            is_online=is_online,
            is_available=is_available
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def accept_chat(self, request, pk=None):
        """Accept a chat session"""
        agent = self.get_object()
        session_id = request.data.get('session_id')

        if not session_id:
            return Response(
                {'error': _('Session ID is required')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            return Response(
                {'error': _('Chat session not found')},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only allow accepting own chats
        if agent.user != request.user:
            return Response(
                {'error': _('Cannot accept chats for other agents')},
                status=status.HTTP_403_FORBIDDEN
            )

        ChatManager.assign_agent(session=session, agent=agent)
        return Response(status=status.HTTP_204_NO_CONTENT) 