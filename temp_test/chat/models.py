from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from model_utils import Choices

class LiveChatSession(TimeStampedModel):
    """Model for managing live chat sessions between users and operators."""
    
    STATUS = Choices(
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('transferred', 'Transferred')
    )
    
    PRIORITY = Choices(
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operated_sessions'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default=STATUS.active
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY,
        default=PRIORITY.medium
    )
    subject = models.CharField(max_length=255)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created']
        verbose_name = 'Live Chat Session'
        verbose_name_plural = 'Live Chat Sessions'
    
    def __str__(self):
        return f'Chat {self.id} - {self.user.username} ({self.status})'

class LiveChatMessage(TimeStampedModel):
    """Model for storing chat messages within a session."""
    
    TYPE = Choices(
        ('text', 'Text'),
        ('file', 'File'),
        ('image', 'Image'),
        ('system', 'System')
    )
    
    session = models.ForeignKey(
        LiveChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_messages'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE,
        default=TYPE.text
    )
    content = models.TextField()
    file = models.FileField(
        upload_to='chat_files/%Y/%m/%d/',
        null=True,
        blank=True
    )
    file_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['created']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        return f'Message from {self.sender.username} in Chat {self.session.id}'

class LiveChatOperator(TimeStampedModel):
    """Model for managing chat operators and their status."""
    
    STATUS = Choices(
        ('online', 'Online'),
        ('busy', 'Busy'),
        ('offline', 'Offline')
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_operator'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default=STATUS.offline
    )
    max_concurrent_sessions = models.PositiveSmallIntegerField(default=3)
    current_sessions = models.PositiveSmallIntegerField(default=0)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Chat Operator'
        verbose_name_plural = 'Chat Operators'
    
    def __str__(self):
        return f'Operator {self.user.username} ({self.status})'

class LiveChatRating(TimeStampedModel):
    """Model for storing chat session ratings and feedback."""
    
    session = models.OneToOneField(
        LiveChatSession,
        on_delete=models.CASCADE,
        related_name='rating'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='given_ratings'
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_ratings'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Chat Rating'
        verbose_name_plural = 'Chat Ratings'
    
    def __str__(self):
        return f'Rating for Chat {self.session.id}: {self.rating}/5'
