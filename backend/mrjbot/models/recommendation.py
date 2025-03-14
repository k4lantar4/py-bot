from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserUsagePattern(models.Model):
    """Model for tracking user usage patterns"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usage_pattern')
    avg_daily_traffic = models.FloatField(_("Average Daily Traffic (GB)"), default=0)
    peak_hours_usage = models.JSONField(_("Peak Hours Usage"), default=dict)
    preferred_locations = models.JSONField(_("Preferred Locations"), default=list)
    connection_stability = models.FloatField(_("Connection Stability %"), default=100)
    usage_frequency = models.IntegerField(_("Usage Days per Month"), default=0)
    last_analyzed = models.DateTimeField(_("Last Analyzed"), auto_now=True)
    
    class Meta:
        verbose_name = _("User Usage Pattern")
        verbose_name_plural = _("User Usage Patterns")
        
    def __str__(self):
        return f"Usage Pattern - {self.user.username}"

class PlanRecommendation(models.Model):
    """Model for storing plan recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plan_recommendations')
    recommended_plan = models.ForeignKey('subscription.Plan', on_delete=models.CASCADE)
    current_plan = models.ForeignKey(
        'subscription.Plan', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='current_recommendations'
    )
    confidence_score = models.FloatField(_("Confidence Score"), default=0)
    reasons = models.JSONField(_("Recommendation Reasons"), default=list)
    is_accepted = models.BooleanField(_("Accepted"), default=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    expires_at = models.DateTimeField(_("Expires At"), null=True)
    
    class Meta:
        verbose_name = _("Plan Recommendation")
        verbose_name_plural = _("Plan Recommendations")
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.recommended_plan.name}"

class RecommendationFeedback(models.Model):
    """Model for tracking recommendation feedback"""
    recommendation = models.OneToOneField(
        PlanRecommendation,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    is_helpful = models.BooleanField(_("Was Helpful"), null=True)
    feedback_text = models.TextField(_("Feedback Text"), blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Recommendation Feedback")
        verbose_name_plural = _("Recommendation Feedbacks")
        
    def __str__(self):
        return f"Feedback on {self.recommendation}" 