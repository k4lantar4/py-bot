import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from ..services.chat import ChatManager
from ..models.chat import ChatSession, ChatAgent


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for chat functionality"""

    async def connect(self):
        """Handle WebSocket connection"""
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        # Get chat session ID from URL route
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group = f"chat_{self.chat_id}"

        # Check if user has access to this chat
        if not await self.can_access_chat():
            await self.close()
            return

        # Add to chat group
        await self.channel_layer.group_add(
            self.chat_group,
            self.channel_name
        )

        # Accept connection
        await self.accept()

        # Mark user as connected
        if await self.is_agent():
            await self.update_agent_status(is_online=True)

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'chat_group'):
            # Remove from chat group
            await self.channel_layer.group_discard(
                self.chat_group,
                self.channel_name
            )

            # Mark agent as offline if applicable
            if await self.is_agent():
                await self.update_agent_status(is_online=False)

    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        data = content.get('data', {})

        try:
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read':
                await self.handle_read()
            elif message_type == 'transfer':
                await self.handle_transfer(data)
            elif message_type == 'close':
                await self.handle_close(data)
            else:
                await self.send_error('Invalid message type')
        except ValidationError as e:
            await self.send_error(str(e))
        except Exception as e:
            await self.send_error(_('An error occurred'))

    async def handle_message(self, data):
        """Handle new chat message"""
        content = data.get('content')
        message_type = data.get('type', 'TEXT')
        file_url = data.get('file_url')
        file_name = data.get('file_name')
        file_size = data.get('file_size')
        metadata = data.get('metadata')

        if not content and not file_url:
            raise ValidationError(_('Message content or file is required'))

        await database_sync_to_async(ChatManager.send_message)(
            session_id=self.chat_id,
            sender=self.scope['user'],
            content=content,
            message_type=message_type,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            metadata=metadata
        )

    async def handle_typing(self, data):
        """Handle typing indicator"""
        is_typing = data.get('is_typing', True)
        await self.channel_layer.group_send(
            self.chat_group,
            {
                'type': 'chat.typing',
                'user': self.scope['user'].username,
                'is_typing': is_typing
            }
        )

    async def handle_read(self):
        """Handle messages read indicator"""
        await database_sync_to_async(ChatManager.mark_messages_read)(
            session_id=self.chat_id,
            user=self.scope['user']
        )

    async def handle_transfer(self, data):
        """Handle chat transfer request"""
        if not await self.is_agent():
            raise ValidationError(_('Only agents can transfer chats'))

        to_agent_id = data.get('to_agent')
        reason = data.get('reason')

        if not to_agent_id or not reason:
            raise ValidationError(_('Agent and reason are required'))

        await database_sync_to_async(ChatManager.transfer_chat)(
            session_id=self.chat_id,
            from_agent=await self.get_agent(),
            to_agent_id=to_agent_id,
            reason=reason
        )

    async def handle_close(self, data):
        """Handle chat close request"""
        rating = data.get('rating')
        feedback = data.get('feedback')

        await database_sync_to_async(ChatManager.close_chat)(
            session_id=self.chat_id,
            rating=rating,
            feedback=feedback
        )

    async def chat_message(self, event):
        """Handle chat.message event"""
        await self.send_json({
            'type': 'message',
            'message': event['message']
        })

    async def chat_typing(self, event):
        """Handle chat.typing event"""
        await self.send_json({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        })

    async def chat_status(self, event):
        """Handle chat.status event"""
        await self.send_json({
            'type': 'status',
            'status': event['status'],
            'agent': event['agent']
        })

    async def chat_transfer(self, event):
        """Handle chat.transfer event"""
        await self.send_json({
            'type': 'transfer',
            'transfer': event['transfer']
        })

    async def chat_read(self, event):
        """Handle chat.read event"""
        await self.send_json({
            'type': 'read',
            'user': event['user']
        })

    async def send_error(self, message):
        """Send error message to client"""
        await self.send_json({
            'type': 'error',
            'message': message
        })

    @database_sync_to_async
    def can_access_chat(self):
        """Check if user can access this chat"""
        try:
            session = ChatSession.objects.get(id=self.chat_id)
            user = self.scope['user']
            return (
                session.user == user or
                ChatAgent.objects.filter(user=user).exists()
            )
        except ChatSession.DoesNotExist:
            return False

    @database_sync_to_async
    def is_agent(self):
        """Check if user is a chat agent"""
        return ChatAgent.objects.filter(
            user=self.scope['user']
        ).exists()

    @database_sync_to_async
    def get_agent(self):
        """Get chat agent for current user"""
        return ChatAgent.objects.get(user=self.scope['user'])

    @database_sync_to_async
    def update_agent_status(self, is_online=None, is_available=None):
        """Update agent's online/available status"""
        if await self.is_agent():
            agent = await self.get_agent()
            ChatManager.update_agent_status(
                agent=agent,
                is_online=is_online,
                is_available=is_available
            ) 