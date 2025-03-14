from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .models import PointsTransaction
from .services import PointsService

@receiver(post_save, sender='payments.Payment')
def add_points_for_payment(sender, instance, created, **kwargs):
    """Add points when a payment is completed."""
    if created and instance.status == 'completed':
        # Calculate points based on payment amount (e.g., 1 point per 1000 toman)
        points = int(instance.amount / 1000)
        if points > 0:
            PointsService.add_points(
                user=instance.user,
                points=points,
                description=_('Points earned from payment #{}').format(instance.id)
            )

@receiver(post_save, sender='v2ray.Subscription')
def add_points_for_subscription(sender, instance, created, **kwargs):
    """Add points when a subscription is created."""
    if created:
        # Calculate points based on subscription duration (e.g., 1 point per day)
        points = instance.duration
        if points > 0:
            PointsService.add_points(
                user=instance.user,
                points=points,
                description=_('Points earned from subscription #{}').format(instance.id)
            )

@receiver(post_save, sender='users.User')
def add_points_for_referral(sender, instance, created, **kwargs):
    """Add points when a user is referred."""
    if created and instance.referrer:
        # Add referral bonus points
        referral_points = 10  # Configure this value
        PointsService.add_points(
            user=instance.referrer,
            points=referral_points,
            description=_('Referral bonus for user {}').format(instance.username)
        ) 