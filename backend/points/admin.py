from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PointsTransaction, PointsRedemptionRule, PointsRedemption

@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    """Admin view for points transactions."""
    list_display = ('user', 'type', 'points', 'description', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(PointsRedemptionRule)
class PointsRedemptionRuleAdmin(admin.ModelAdmin):
    """Admin view for points redemption rules."""
    list_display = ('name', 'points_required', 'reward_type', 'reward_value', 'is_active', 'created_at')
    list_filter = ('is_active', 'reward_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('points_required', 'reward_type')
        return self.readonly_fields

@admin.register(PointsRedemption)
class PointsRedemptionAdmin(admin.ModelAdmin):
    """Admin view for points redemptions."""
    list_display = ('user', 'rule', 'points_spent', 'reward_value', 'created_at')
    list_filter = ('created_at', 'rule')
    search_fields = ('user__username', 'rule__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'rule') 