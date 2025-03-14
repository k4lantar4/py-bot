from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum

from ..models.points import (
    PointsConfig, PointsTransaction, Reward,
    RewardRedemption, UserPoints
)
from ..utils.telegram import send_admin_notification

class PointsManager:
    """Service class for managing points and rewards"""

    @classmethod
    def award_points(cls, user, action: str, points: int = None,
                    description: str = None, performed_by = None,
                    reference: str = None, metadata: Dict = None) -> PointsTransaction:
        """Award points to a user for an action"""
        with transaction.atomic():
            # Get points configuration if points not specified
            if points is None:
                try:
                    config = PointsConfig.objects.get(action=action, is_active=True)
                    points = config.points
                    description = description or config.description
                except PointsConfig.DoesNotExist:
                    raise ValidationError(_('Invalid action or points configuration'))

            # Check cooldown and daily limits
            if config:
                now = timezone.now()
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

                # Check cooldown
                if config.cooldown_minutes > 0:
                    cooldown_start = now - timezone.timedelta(minutes=config.cooldown_minutes)
                    if PointsTransaction.objects.filter(
                        user=user,
                        action=action,
                        created_at__gte=cooldown_start
                    ).exists():
                        raise ValidationError(_('Action is in cooldown period'))

                # Check daily limit
                if config.max_daily:
                    daily_points = PointsTransaction.objects.filter(
                        user=user,
                        action=action,
                        created_at__gte=today_start
                    ).aggregate(total=Sum('points'))['total'] or 0
                    if daily_points + points > config.max_daily:
                        raise ValidationError(_('Daily points limit exceeded'))

            # Create transaction
            transaction = PointsTransaction.objects.create(
                user=user,
                points=points,
                transaction_type='EARNED',
                action=action,
                description=description or f'Points earned for {action}',
                reference=reference or '',
                performed_by=performed_by,
                metadata=metadata or {}
            )

            # Update user points
            user_points, _ = UserPoints.objects.get_or_create(user=user)
            user_points.recalculate_balance()

            # Notify user via Telegram
            cls._notify_points_earned(user, points, action)

            return transaction

    @classmethod
    def deduct_points(cls, user, points: int, reason: str,
                     performed_by = None, metadata: Dict = None) -> PointsTransaction:
        """Deduct points from a user"""
        with transaction.atomic():
            user_points, _ = UserPoints.objects.get_or_create(user=user)
            if user_points.current_balance < points:
                raise ValidationError(_('Insufficient points balance'))

            transaction = PointsTransaction.objects.create(
                user=user,
                points=points,
                transaction_type='SPENT',
                action='manual_deduction',
                description=reason,
                performed_by=performed_by,
                metadata=metadata or {}
            )

            user_points.recalculate_balance()
            return transaction

    @classmethod
    def redeem_reward(cls, user, reward: Reward,
                     metadata: Dict = None) -> RewardRedemption:
        """Redeem points for a reward"""
        with transaction.atomic():
            if not reward.is_available():
                raise ValidationError(_('Reward is not available'))

            user_points, _ = UserPoints.objects.get_or_create(user=user)
            if user_points.current_balance < reward.points_required:
                raise ValidationError(_('Insufficient points balance'))

            # Create redemption record
            redemption = RewardRedemption.objects.create(
                user=user,
                reward=reward,
                points_spent=reward.points_required,
                metadata=metadata or {}
            )

            # Deduct points
            PointsTransaction.objects.create(
                user=user,
                points=reward.points_required,
                transaction_type='SPENT',
                action='reward_redemption',
                description=f'Redeemed reward: {reward.name}',
                reference=str(redemption.id),
                metadata={'reward_id': reward.id}
            )

            user_points.recalculate_balance()

            # Notify admins
            send_admin_notification(
                f"🎁 New reward redemption:\n"
                f"User: {user.username}\n"
                f"Reward: {reward.name}\n"
                f"Points: {reward.points_required}"
            )

            return redemption

    @classmethod
    def approve_redemption(cls, redemption: RewardRedemption,
                         approved_by, notes: str = None) -> RewardRedemption:
        """Approve a reward redemption"""
        with transaction.atomic():
            if redemption.status != 'PENDING':
                raise ValidationError(_('Redemption is not pending'))

            redemption.status = 'APPROVED'
            redemption.approved_by = approved_by
            redemption.approved_at = timezone.now()
            if notes:
                redemption.notes = notes
            redemption.save()

            # Process reward
            cls._process_reward(redemption)

            # Notify user
            cls._notify_reward_approved(redemption)

            return redemption

    @classmethod
    def reject_redemption(cls, redemption: RewardRedemption,
                         rejected_by, reason: str) -> RewardRedemption:
        """Reject a reward redemption and refund points"""
        with transaction.atomic():
            if redemption.status != 'PENDING':
                raise ValidationError(_('Redemption is not pending'))

            # Refund points
            PointsTransaction.objects.create(
                user=redemption.user,
                points=redemption.points_spent,
                transaction_type='EARNED',
                action='redemption_refund',
                description=f'Refund for rejected reward: {redemption.reward.name}',
                reference=str(redemption.id)
            )

            # Update redemption
            redemption.status = 'REJECTED'
            redemption.approved_by = rejected_by
            redemption.approved_at = timezone.now()
            redemption.notes = reason
            redemption.save()

            # Update user points
            user_points = UserPoints.objects.get(user=redemption.user)
            user_points.recalculate_balance()

            # Notify user
            cls._notify_reward_rejected(redemption)

            return redemption

    @classmethod
    def get_user_points_summary(cls, user) -> Dict:
        """Get summary of user's points"""
        user_points, _ = UserPoints.objects.get_or_create(user=user)
        now = timezone.now()

        # Get points expiring soon
        expiring_soon = PointsTransaction.objects.filter(
            user=user,
            transaction_type__in=['EARNED', 'BONUS', 'REFERRAL'],
            expires_at__gt=now,
            expires_at__lte=now + timezone.timedelta(days=30)
        ).aggregate(total=Sum('points'))['total'] or 0

        # Get recent transactions
        recent_transactions = PointsTransaction.objects.filter(
            user=user
        ).order_by('-created_at')[:5]

        return {
            'current_balance': user_points.current_balance,
            'total_earned': user_points.total_earned,
            'total_spent': user_points.total_spent,
            'expiring_soon': expiring_soon,
            'recent_transactions': [
                {
                    'points': t.points,
                    'type': t.transaction_type,
                    'description': t.description,
                    'date': t.created_at
                }
                for t in recent_transactions
            ]
        }

    @classmethod
    def get_available_rewards(cls, user) -> List[Dict]:
        """Get list of rewards available to the user"""
        now = timezone.now()
        user_points = UserPoints.objects.get(user=user)

        rewards = Reward.objects.filter(
            is_active=True,
            start_date__lte=now,
            Q(end_date__isnull=True) | Q(end_date__gt=now),
            Q(quantity_available__isnull=True) | Q(quantity_available__gt=0)
        ).order_by('points_required')

        return [
            {
                'id': reward.id,
                'name': reward.name,
                'description': reward.description,
                'points_required': reward.points_required,
                'can_redeem': user_points.current_balance >= reward.points_required,
                'reward_type': reward.reward_type,
                'quantity_available': reward.quantity_available
            }
            for reward in rewards
        ]

    @classmethod
    def _process_reward(cls, redemption: RewardRedemption) -> None:
        """Process approved reward based on type"""
        reward = redemption.reward
        user = redemption.user

        if reward.reward_type == 'DISCOUNT':
            # Apply service discount
            discount_percent = reward.reward_data.get('discount_percent', 0)
            # TODO: Apply discount to user's next purchase

        elif reward.reward_type == 'TRAFFIC':
            # Add extra traffic
            extra_gb = reward.reward_data.get('traffic_gb', 0)
            # TODO: Add traffic to user's account

        elif reward.reward_type == 'TIME':
            # Add extra time
            extra_days = reward.reward_data.get('extra_days', 0)
            # TODO: Extend user's subscription

        elif reward.reward_type == 'VIP':
            # Grant VIP status
            vip_days = reward.reward_data.get('vip_days', 30)
            # TODO: Grant VIP status to user

    @classmethod
    def _notify_points_earned(cls, user, points: int, action: str) -> None:
        """Send notification to user about earned points"""
        # TODO: Implement user notification via Telegram
        pass

    @classmethod
    def _notify_reward_approved(cls, redemption: RewardRedemption) -> None:
        """Send notification to user about approved reward"""
        # TODO: Implement user notification via Telegram
        pass

    @classmethod
    def _notify_reward_rejected(cls, redemption: RewardRedemption) -> None:
        """Send notification to user about rejected reward"""
        # TODO: Implement user notification via Telegram
        pass 