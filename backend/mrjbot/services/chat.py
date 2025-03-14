from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, F
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models.chat import (
    ChatAgent, ChatSession, ChatMessage,
    ChatQueueEntry, ChatTransfer
)
from ..utils.telegram import send_admin_notification

channel_layer = get_channel_layer()

class ChatManager:
    """Service class for managing chat operations"""

    @classmethod
    def start_chat(cls, user, subject: str, category: str,
                  language: str = 'fa', priority: int = 2,
                  specialties: List[str] = None,
                  user_data: Dict = None) -> ChatSession:
        """Start a new chat session"""
        with transaction.atomic():
            # Create chat session
            session = ChatSession.objects.create(
                user=user,
                subject=subject,
                category=category,
                language=language,
                priority=priority,
                user_data=user_data or {}
            )

            # Create queue entry
            queue_entry = ChatQueueEntry.objects.create(
                session=session,
                priority=priority,
                required_language=language,
                required_specialties=specialties or []
            )

            # Try to find an available agent immediately
            agent = queue_entry.find_available_agent()
            if agent:
                cls._assign_agent(session, agent)
            else:
                # Notify admins about waiting chat
                send_admin_notification(
                    f"💬 New chat waiting:\n"
                    f"User: {user.username}\n"
                    f"Subject: {subject}\n"
                    f"Category: {category}"
                )

            return session

    @classmethod
    def send_message(cls, session: ChatSession, sender,
                    content: str, message_type: str = 'TEXT',
                    file_url: str = None, file_name: str = None,
                    file_size: int = None, metadata: Dict = None) -> ChatMessage:
        """Send a message in a chat session"""
        if session.status not in ['ACTIVE', 'WAITING']:
            raise ValidationError(_('Cannot send message in inactive chat'))

        message = ChatMessage.objects.create(
            session=session,
            sender=sender,
            content=content,
            message_type=message_type,
            file_url=file_url or '',
            file_name=file_name or '',
            file_size=file_size,
            metadata=metadata or {}
        )

        # Send real-time update
        cls._broadcast_message(message)

        return message

    @classmethod
    def assign_agent(cls, session: ChatSession, agent: ChatAgent) -> None:
        """Assign an agent to a chat session"""
        with transaction.atomic():
            if session.status != 'WAITING':
                raise ValidationError(_('Chat is not waiting for agent'))
            if not agent.can_accept_chat():
                raise ValidationError(_('Agent cannot accept more chats'))

            cls._assign_agent(session, agent)

    @classmethod
    def transfer_chat(cls, session: ChatSession, from_agent: ChatAgent,
                     to_agent: ChatAgent, reason: str) -> ChatTransfer:
        """Transfer a chat to another agent"""
        with transaction.atomic():
            if session.status != 'ACTIVE':
                raise ValidationError(_('Cannot transfer inactive chat'))
            if session.agent != from_agent:
                raise ValidationError(_('Chat is not assigned to this agent'))
            if not to_agent.can_accept_chat():
                raise ValidationError(_('Target agent cannot accept more chats'))

            # Create transfer record
            transfer = ChatTransfer.objects.create(
                session=session,
                from_agent=from_agent,
                to_agent=to_agent,
                reason=reason
            )

            # Update session status
            session.status = 'TRANSFERRED'
            session.save()

            # Send real-time update
            cls._broadcast_transfer(transfer)

            return transfer

    @classmethod
    def close_chat(cls, session: ChatSession, rating: int = None,
                  feedback: str = None) -> None:
        """Close a chat session"""
        session.close(rating=rating, feedback=feedback)

        # Send real-time update
        cls._broadcast_chat_status(session)

        # Notify if rated
        if rating:
            send_admin_notification(
                f"⭐ Chat rated:\n"
                f"Chat ID: {session.id}\n"
                f"Rating: {rating}/5\n"
                f"Agent: {session.agent.user.username if session.agent else 'N/A'}"
            )

    @classmethod
    def get_agent_chats(cls, agent: ChatAgent,
                       status: List[str] = None) -> List[ChatSession]:
        """Get chat sessions for an agent"""
        query = agent.chat_sessions
        if status:
            query = query.filter(status__in=status)
        return query.order_by('-started_at')

    @classmethod
    def get_user_chats(cls, user,
                      status: List[str] = None) -> List[ChatSession]:
        """Get chat sessions for a user"""
        query = user.chat_sessions
        if status:
            query = query.filter(status__in=status)
        return query.order_by('-started_at')

    @classmethod
    def get_chat_messages(cls, session: ChatSession,
                         limit: int = None,
                         before: timezone.datetime = None) -> List[ChatMessage]:
        """Get messages from a chat session"""
        query = session.messages
        if before:
            query = query.filter(sent_at__lt=before)
        if limit:
            query = query[:limit]
        return query.order_by('-sent_at')

    @classmethod
    def mark_messages_read(cls, session: ChatSession,
                         user) -> int:
        """Mark messages as read for a user"""
        # Mark messages from other users as read
        count = session.messages.filter(
            sender__ne=user,
            is_read=False
        ).update(is_read=True)

        if count > 0:
            # Send real-time update
            cls._broadcast_messages_read(session, user)

        return count

    @classmethod
    def update_agent_status(cls, agent: ChatAgent,
                          is_online: bool = None,
                          is_available: bool = None) -> None:
        """Update agent's online/available status"""
        update_fields = []
        if is_online is not None:
            agent.is_online = is_online
            update_fields.append('is_online')
        if is_available is not None:
            agent.is_available = is_available
            update_fields.append('is_available')

        if update_fields:
            agent.save(update_fields=update_fields)
            # Send real-time update
            cls._broadcast_agent_status(agent)

    @classmethod
    def _assign_agent(cls, session: ChatSession, agent: ChatAgent) -> None:
        """Internal method to assign an agent to a session"""
        session.agent = agent
        session.status = 'ACTIVE'
        session.save()

        # Update agent stats
        agent.current_chats += 1
        agent.total_chats_handled += 1
        agent.save()

        # Remove from queue if present
        ChatQueueEntry.objects.filter(session=session).delete()

        # Send system message
        cls.send_message(
            session=session,
            sender=None,
            content=_('Agent {username} joined the chat').format(
                username=agent.user.username
            ),
            message_type='SYSTEM'
        )

        # Send real-time update
        cls._broadcast_chat_status(session)

    @classmethod
    def _broadcast_message(cls, message: ChatMessage) -> None:
        """Broadcast a new message to chat participants"""
        async_to_sync(channel_layer.group_send)(
            f"chat_{message.session.id}",
            {
                "type": "chat.message",
                "message": {
                    "id": message.id,
                    "sender": message.sender.username if message.sender else None,
                    "content": message.content,
                    "type": message.message_type,
                    "file_url": message.file_url,
                    "file_name": message.file_name,
                    "sent_at": message.sent_at.isoformat(),
                }
            }
        )

    @classmethod
    def _broadcast_chat_status(cls, session: ChatSession) -> None:
        """Broadcast chat status update"""
        async_to_sync(channel_layer.group_send)(
            f"chat_{session.id}",
            {
                "type": "chat.status",
                "status": session.status,
                "agent": session.agent.user.username if session.agent else None
            }
        )

    @classmethod
    def _broadcast_transfer(cls, transfer: ChatTransfer) -> None:
        """Broadcast chat transfer update"""
        async_to_sync(channel_layer.group_send)(
            f"chat_{transfer.session.id}",
            {
                "type": "chat.transfer",
                "transfer": {
                    "from_agent": transfer.from_agent.user.username,
                    "to_agent": transfer.to_agent.user.username,
                    "status": transfer.status
                }
            }
        )

    @classmethod
    def _broadcast_messages_read(cls, session: ChatSession, user) -> None:
        """Broadcast messages read update"""
        async_to_sync(channel_layer.group_send)(
            f"chat_{session.id}",
            {
                "type": "chat.read",
                "user": user.username
            }
        )

    @classmethod
    def _broadcast_agent_status(cls, agent: ChatAgent) -> None:
        """Broadcast agent status update"""
        async_to_sync(channel_layer.group_send)(
            "chat_agents",
            {
                "type": "agent.status",
                "agent": {
                    "username": agent.user.username,
                    "is_online": agent.is_online,
                    "is_available": agent.is_available,
                    "current_chats": agent.current_chats
                }
            }
        ) 