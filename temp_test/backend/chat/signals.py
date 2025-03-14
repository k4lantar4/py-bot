from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import LiveChatSession, LiveChatMessage, LiveChatOperator, LiveChatRating

@receiver(post_save, sender=LiveChatSession)
def handle_session_status_change(sender, instance, created, **kwargs):
    if not created and instance.tracker.has_changed('status'):
        # If session is closed, update operator's current sessions
        if instance.status == LiveChatSession.Status.CLOSED and instance.operator:
            operator = instance.operator.operator_profile
            operator.current_sessions = max(0, operator.current_sessions - 1)
            operator.save()

@receiver(post_save, sender=LiveChatMessage)
def handle_new_message(sender, instance, created, **kwargs):
    if created:
        # Update session's updated_at timestamp
        instance.session.updated_at = timezone.now()
        instance.session.save()

@receiver(post_save, sender=LiveChatOperator)
def handle_operator_status_change(sender, instance, created, **kwargs):
    if not created and instance.tracker.has_changed('status'):
        # If operator goes offline, close their active sessions
        if instance.status == LiveChatOperator.Status.OFFLINE:
            active_sessions = LiveChatSession.objects.filter(
                operator=instance.user,
                status=LiveChatSession.Status.ACTIVE
            )
            for session in active_sessions:
                session.status = LiveChatSession.Status.CLOSED
                session.closed_at = timezone.now()
                session.save()

@receiver(post_delete, sender=LiveChatSession)
def handle_session_deletion(sender, instance, **kwargs):
    # Update operator's current sessions when a session is deleted
    if instance.operator:
        operator = instance.operator.operator_profile
        operator.current_sessions = max(0, operator.current_sessions - 1)
        operator.save() 