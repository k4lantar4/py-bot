from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import LiveChatSession, LiveChatMessage, LiveChatOperator

@receiver(post_save, sender=LiveChatSession)
def handle_chat_session_status(sender, instance, created, **kwargs):
    """Handle chat session status changes."""
    if not created and instance.status == 'closed' and not instance.closed_at:
        # Update closed_at timestamp when session is closed
        instance.closed_at = timezone.now()
        instance.save(update_fields=['closed_at'])
        
        # Update operator's current sessions count
        if instance.operator:
            operator = instance.operator.chat_operator
            if operator.current_sessions > 0:
                operator.current_sessions -= 1
                operator.save(update_fields=['current_sessions'])

@receiver(post_save, sender=LiveChatMessage)
def handle_new_message(sender, instance, created, **kwargs):
    """Handle new message creation."""
    if created and instance.session.status == 'closed':
        # Reopen session if a new message is sent in a closed session
        instance.session.status = 'active'
        instance.session.closed_at = None
        instance.session.save(update_fields=['status', 'closed_at'])

@receiver(pre_save, sender=LiveChatOperator)
def handle_operator_status(sender, instance, **kwargs):
    """Handle operator status changes."""
    if not instance.pk:  # New operator
        return
    
    old_instance = LiveChatOperator.objects.get(pk=instance.pk)
    
    # Update last_active when status changes
    if old_instance.status != instance.status:
        instance.last_active = timezone.now()
    
    # Set status to busy if max sessions reached
    if instance.current_sessions >= instance.max_concurrent_sessions:
        instance.status = 'busy'
    # Set status back to online if sessions available and status was busy
    elif instance.status == 'busy' and instance.current_sessions < instance.max_concurrent_sessions:
        instance.status = 'online' 