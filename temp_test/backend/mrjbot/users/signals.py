from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, UserRole

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile for each new user.
    """
    if created:
        Profile.objects.create(user=instance)
        
        # Send welcome email
        if not instance.is_superuser:
            send_mail(
                _('Welcome to MRJ Bot!'),
                _('Thank you for joining MRJ Bot. We hope you enjoy our services.'),
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False,
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the user's profile whenever the user is saved.
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """
    Assign default role to new users.
    """
    if created and not instance.is_superuser:
        from .models import Role
        default_role, _ = Role.objects.get_or_create(
            name='customer',
            defaults={'description': 'Default customer role'}
        )
        UserRole.objects.create(
            user=instance,
            role=default_role,
            assigned_by=instance
        )

@receiver(post_save, sender=User)
def update_referral_points(sender, instance, created, **kwargs):
    """
    Update referral points when a new user is created.
    """
    if created and instance.referred_by:
        # Add points to referrer
        instance.referred_by.points += 100  # Example: 100 points per referral
        instance.referred_by.save()
        
        # Send notification to referrer
        from mrjbot.notifications.models import Notification
        Notification.objects.create(
            user=instance.referred_by,
            title=_('New Referral!'),
            message=_('You received 100 points for referring a new user.'),
            type='referral'
        )

@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    """
    Send verification email to new users.
    """
    if created and not instance.is_superuser and not instance.is_email_verified:
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = default_token_generator.make_token(instance)
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"
        
        send_mail(
            _('Verify your email address'),
            _('Please click the following link to verify your email address: {}').format(verification_url),
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )

@receiver(post_save, sender=User)
def update_user_status(sender, instance, **kwargs):
    """
    Update user status and send notifications.
    """
    if instance.is_active and not instance.is_email_verified:
        from mrjbot.notifications.models import Notification
        Notification.objects.create(
            user=instance,
            title=_('Account Activated'),
            message=_('Your account has been activated. Please verify your email address.'),
            type='account'
        ) 