class UsagePatternAnalyzer:
    """Service for analyzing user usage patterns and generating plan suggestions."""
    
    @staticmethod
    def analyze_usage(user):
        """Analyze user's usage patterns."""
        subscriptions = user.subscriptions.filter(status='active')
        if not subscriptions:
            return None
            
        total_usage = sum(sub.data_usage_gb for sub in subscriptions)
        days_active = (timezone.now() - subscriptions.first().start_date).days
        
        if days_active == 0:
            return None
            
        average_daily = total_usage / days_active
        
        # Analyze peak hours from usage logs
        peak_hours = UsagePatternAnalyzer._get_peak_hours(user)
        
        # Get preferred protocols
        preferred_protocols = UsagePatternAnalyzer._get_preferred_protocols(user)
        
        return {
            'average_daily_usage_gb': average_daily,
            'peak_hours': peak_hours,
            'preferred_protocols': preferred_protocols
        }
    
    @staticmethod
    def _get_peak_hours(user):
        """Get hours with highest usage."""
        # Implementation for analyzing peak usage hours
        # This would typically query usage logs and aggregate by hour
        return []
    
    @staticmethod
    def _get_preferred_protocols(user):
        """Get user's preferred protocols."""
        # Implementation for analyzing protocol preferences
        # This would typically query connection logs and count protocol usage
        return []

class PlanSuggestionService:
    """Service for generating and managing plan suggestions."""
    
    @staticmethod
    def generate_suggestion(user):
        """Generate a plan suggestion based on usage patterns."""
        usage_pattern = user.usage_pattern
        if not usage_pattern:
            return None
            
        current_plan = user.subscriptions.filter(status='active').first()
        if not current_plan:
            return None
            
        # Find suitable plans based on usage
        suitable_plans = Plan.objects.filter(
            data_limit_gb__gte=usage_pattern.average_daily_usage_gb * 30  # Monthly usage
        ).exclude(id=current_plan.plan.id)
        
        if not suitable_plans:
            return None
            
        # Select the most suitable plan
        suggested_plan = suitable_plans.first()
        
        # Generate reason for suggestion
        reason = PlanSuggestionService._generate_reason(
            current_plan,
            suggested_plan,
            usage_pattern
        )
        
        # Create suggestion
        return PlanSuggestion.objects.create(
            user=user,
            suggested_plan=suggested_plan,
            reason=reason
        )
    
    @staticmethod
    def _generate_reason(current_plan, suggested_plan, usage_pattern):
        """Generate a reason for the plan suggestion."""
        current_daily = current_plan.data_limit_gb / 30
        suggested_daily = suggested_plan.data_limit_gb / 30
        
        if suggested_daily > current_daily:
            return f"با توجه به مصرف روزانه شما ({usage_pattern.average_daily_usage_gb:.1f}GB)، پلن {suggested_plan.name} با {suggested_plan.data_limit_gb}GB ترافیک ماهانه برای شما مناسب‌تر است."
        else:
            return f"با توجه به مصرف روزانه شما ({usage_pattern.average_daily_usage_gb:.1f}GB)، پلن {suggested_plan.name} با {suggested_plan.data_limit_gb}GB ترافیک ماهانه برای شما مقرون به صرفه‌تر است." 