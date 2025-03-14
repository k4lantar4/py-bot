from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q

User = get_user_model()

class ChatAgent(models.Model):
    """Model for chat support agents"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_agent')
    is_online = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    max_concurrent_chats = models.IntegerField(default=3)
    languages = models.JSONField(default=list)  # List of language codes
    specialties = models.JSONField(default=list)  # List of specialties
    current_chats = models.IntegerField(default=0)
    total_chats_handled = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('chat agent')
        verbose_name_plural = _('chat agents')

    def __str__(self):
        return f"{self.user.username} ({self.current_chats}/{self.max_concurrent_chats})"

    def can_accept_chat(self) -> bool:
        """Check if agent can accept a new chat"""
        return (
            self.is_online and
            self.is_available and
            self.current_chats < self.max_concurrent_chats
        )

class ChatSession(models.Model):
    """Model for chat sessions"""
    STATUS_CHOICES = [
        ('WAITING', 'Waiting for Agent'),
        ('ACTIVE', 'Active'),
        ('TRANSFERRED', 'Transferred'),
        ('CLOSED', 'Closed'),
        ('TIMEOUT', 'Timed Out'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Normal'),
        (3, 'High'),
        (4, 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    agent = models.ForeignKey(ChatAgent, on_delete=models.SET_NULL, null=True, related_name='chat_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    subject = models.CharField(max_length=200)
    language = models.CharField(max_length=10, default='fa')  # ISO 639-1 language code
    category = models.CharField(max_length=50, choices=[
        ('GENERAL', 'General Support'),
        ('TECHNICAL', 'Technical Support'),
        ('BILLING', 'Billing Support'),
        ('VIP', 'VIP Support'),
    ])
    user_data = models.JSONField(default=dict)  # Additional user data
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_message_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    tags = models.JSONField(default=list)

    class Meta:
        ordering = ['-started_at']
        verbose_name = _('chat session')
        verbose_name_plural = _('chat sessions')

    def __str__(self):
        return f"Chat {self.id} - {self.user.username} ({self.status})"

    def close(self, rating: int = None, feedback: str = None):
        """Close the chat session"""
        if self.status not in ['ACTIVE', 'TRANSFERRED']:
            raise ValidationError(_('Cannot close a chat that is not active'))

        self.status = 'CLOSED'
        self.ended_at = timezone.now()
        if rating is not None:
            self.rating = rating
        if feedback:
            self.feedback = feedback
        self.save()

        # Update agent stats
        if self.agent:
            self.agent.current_chats -= 1
            if rating:
                total_rated = self.agent.chat_sessions.exclude(rating__isnull=True).count()
                self.agent.average_rating = (
                    (self.agent.average_rating * total_rated + rating) /
                    (total_rated + 1)
                )
            self.agent.save()

class ChatMessage(models.Model):
    """Model for chat messages"""
    MESSAGE_TYPES = [
        ('TEXT', 'Text Message'),
        ('IMAGE', 'Image'),
        ('FILE', 'File'),
        ('SYSTEM', 'System Message'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='chat_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='TEXT')
    content = models.TextField()
    file_url = models.URLField(blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']
        verbose_name = _('chat message')
        verbose_name_plural = _('chat messages')

    def __str__(self):
        return f"Message from {self.sender.username} in Chat {self.session.id}"

    def save(self, *args, **kwargs):
        # Update session's last_message_at
        self.session.last_message_at = timezone.now()
        self.session.save()
        super().save(*args, **kwargs)

class ChatQueueEntry(models.Model):
    """Model for managing chat queue"""
    session = models.OneToOneField(ChatSession, on_delete=models.CASCADE, related_name='queue_entry')
    priority = models.IntegerField(choices=ChatSession.PRIORITY_CHOICES, default=2)
    required_specialties = models.JSONField(default=list)
    required_language = models.CharField(max_length=10)
    entered_at = models.DateTimeField(auto_now_add=True)
    last_try_at = models.DateTimeField(auto_now_add=True)
    tries = models.IntegerField(default=0)

    class Meta:
        ordering = ['-priority', 'entered_at']
        verbose_name = _('chat queue entry')
        verbose_name_plural = _('chat queue entries')

    def __str__(self):
        return f"Queue entry for Chat {self.session.id}"

    def find_available_agent(self) -> ChatAgent:
        """Find an available agent for this chat"""
        now = timezone.now()
        available_agents = ChatAgent.objects.filter(
            is_online=True,
            is_available=True,
            current_chats__lt=F('max_concurrent_chats'),
            languages__contains=[self.required_language]
        )

        if self.required_specialties:
            available_agents = available_agents.filter(
                specialties__overlap=self.required_specialties
            )

        # Sort by current load and total chats handled
        return available_agents.order_by(
            'current_chats',
            '-total_chats_handled'
        ).first()

class ChatTransfer(models.Model):
    """Model for tracking chat transfers between agents"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='transfers')
    from_agent = models.ForeignKey(ChatAgent, on_delete=models.SET_NULL, null=True, related_name='transfers_from')
    to_agent = models.ForeignKey(ChatAgent, on_delete=models.SET_NULL, null=True, related_name='transfers_to')
    reason = models.TextField()
    transferred_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('TIMEOUT', 'Timed Out'),
    ], default='PENDING')

    class Meta:
        ordering = ['-transferred_at']
        verbose_name = _('chat transfer')
        verbose_name_plural = _('chat transfers')

    def __str__(self):
        return f"Transfer of Chat {self.session.id} from {self.from_agent} to {self.to_agent}"

    def accept(self):
        """Accept the transfer"""
        if self.status != 'PENDING':
            raise ValidationError(_('Transfer is not pending'))

        self.status = 'ACCEPTED'
        self.accepted_at = timezone.now()
        self.save()

        # Update session
        self.session.agent = self.to_agent
        self.session.status = 'ACTIVE'
        self.session.save()

        # Update agent stats
        if self.from_agent:
            self.from_agent.current_chats -= 1
            self.from_agent.save()
        self.to_agent.current_chats += 1
        self.to_agent.save() 