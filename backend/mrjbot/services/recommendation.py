from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Avg, Count, F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..models.recommendation import (
    UserUsagePattern, PlanRecommendation, RecommendationFeedback
)
from ..models.subscription import Plan, Subscription
from ..utils.telegram import send_user_notification

class RecommendationManager:
    """Service class for managing plan recommendations"""

    @classmethod
    def analyze_usage_pattern(cls, user) -> UserUsagePattern:
        """Analyze user's usage pattern"""
        # Get user's subscriptions and traffic data
        subscriptions = Subscription.objects.filter(user=user)
        if not subscriptions.exists():
            return None

        # Calculate metrics
        now = timezone.now()
        month_ago = now - timedelta(days=30)
        
        traffic_data = subscriptions.filter(
            created_at__gte=month_ago
        ).aggregate(
            avg_daily=Avg('daily_traffic'),
            total_days=Count('id', distinct=True)
        )

        # Get peak hours usage
        peak_hours = {
            str(hour): subscriptions.filter(
                last_connected_at__hour=hour
            ).count()
            for hour in range(24)
        }

        # Get preferred locations
        locations = list(subscriptions.values(
            'server__country'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:3])

        # Calculate connection stability
        stability = subscriptions.aggregate(
            avg_stability=Avg('connection_stability')
        )['avg_stability'] or 100

        # Update or create usage pattern
        pattern, _ = UserUsagePattern.objects.update_or_create(
            user=user,
            defaults={
                'avg_daily_traffic': traffic_data['avg_daily'] or 0,
                'peak_hours_usage': peak_hours,
                'preferred_locations': [loc['server__country'] for loc in locations],
                'connection_stability': stability,
                'usage_frequency': traffic_data['total_days'] or 0
            }
        )

        return pattern

    @classmethod
    def generate_recommendations(cls, user) -> List[PlanRecommendation]:
        """Generate plan recommendations for a user"""
        pattern = cls.analyze_usage_pattern(user)
        if not pattern:
            return []

        current_plan = Subscription.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()

        # Get all available plans
        available_plans = Plan.objects.filter(is_active=True)
        recommendations = []

        for plan in available_plans:
            if current_plan and plan.id == current_plan.plan.id:
                continue

            score, reasons = cls._calculate_plan_fit(pattern, plan)
            if score >= 0.6:  # Only recommend if confidence is high enough
                recommendation = PlanRecommendation.objects.create(
                    user=user,
                    recommended_plan=plan,
                    current_plan=current_plan.plan if current_plan else None,
                    confidence_score=score,
                    reasons=reasons,
                    expires_at=timezone.now() + timedelta(days=7)
                )
                recommendations.append(recommendation)

        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)

        # Notify user if we have recommendations
        if recommendations:
            cls._notify_user_recommendations(user, recommendations[0])

        return recommendations

    @classmethod
    def _calculate_plan_fit(cls, pattern: UserUsagePattern, plan: Plan) -> tuple:
        """Calculate how well a plan fits user's usage pattern"""
        reasons = []
        score_components = []

        # Traffic match score (30%)
        daily_traffic_score = min(pattern.avg_daily_traffic / plan.monthly_traffic * 30, 1)
        score_components.append(daily_traffic_score * 0.3)
        
        if daily_traffic_score < 0.8:
            reasons.append(_("Plan provides sufficient traffic for your usage"))
        elif daily_traffic_score > 0.9:
            reasons.append(_("You might need more traffic than this plan offers"))

        # Usage frequency match (20%)
        frequency_score = min(pattern.usage_frequency / 30, 1)
        score_components.append(frequency_score * 0.2)
        
        if frequency_score > 0.8:
            reasons.append(_("Suitable for your daily usage pattern"))

        # Location availability (20%)
        available_locations = set(plan.available_locations)
        preferred_locations = set(pattern.preferred_locations)
        location_score = len(preferred_locations.intersection(available_locations)) / max(len(preferred_locations), 1)
        score_components.append(location_score * 0.2)
        
        if location_score > 0.7:
            reasons.append(_("Available in your preferred locations"))

        # Price optimization (30%)
        if pattern.avg_daily_traffic > 0:
            price_per_gb = plan.price / plan.monthly_traffic
            price_score = min(2 - price_per_gb / 0.5, 1)  # Assume 0.5 is average price/GB
            score_components.append(price_score * 0.3)
            
            if price_score > 0.8:
                reasons.append(_("Good value for your usage"))

        total_score = sum(score_components)
        return total_score, reasons

    @classmethod
    def record_feedback(cls, recommendation: PlanRecommendation,
                       is_helpful: bool, feedback_text: str = None) -> RecommendationFeedback:
        """Record user feedback for a recommendation"""
        feedback, _ = RecommendationFeedback.objects.update_or_create(
            recommendation=recommendation,
            defaults={
                'is_helpful': is_helpful,
                'feedback_text': feedback_text or ''
            }
        )
        return feedback

    @classmethod
    def get_user_recommendations(cls, user,
                               active_only: bool = True) -> List[PlanRecommendation]:
        """Get recommendations for a user"""
        query = PlanRecommendation.objects.filter(user=user)
        if active_only:
            query = query.filter(
                expires_at__gt=timezone.now()
            )
        return query.order_by('-confidence_score')

    @classmethod
    def _notify_user_recommendations(cls, user, recommendation: PlanRecommendation) -> None:
        """Send notification to user about new recommendations"""
        message = (
            f"🎯 پیشنهاد ویژه برای شما!\n\n"
            f"با توجه به الگوی مصرف شما، پلن {recommendation.recommended_plan.name} "
            f"می‌تونه انتخاب مناسبی باشه:\n\n"
        )

        for reason in recommendation.reasons:
            message += f"✅ {reason}\n"

        message += f"\n💰 قیمت: {recommendation.recommended_plan.price:,} تومان"
        
        send_user_notification(user, message) 