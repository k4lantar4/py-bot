from django.contrib import admin

# Register your models here.

@admin.register(PointsRedemptionRule)
class PointsRedemptionRuleAdmin(admin.ModelAdmin):
    """Admin view for points redemption rules."""
    list_display = ('name', 'points_required', 'reward_type', 'reward_value', 'is_active', 'created_at')
    list_filter = ('is_active', 'reward_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(PointsRedemption)
class PointsRedemptionAdmin(admin.ModelAdmin):
    """Admin view for points redemptions."""
    list_display = ('user', 'rule', 'points_spent', 'reward_value', 'created_at')
    list_filter = ('created_at', 'rule')
    search_fields = ('user__username', 'rule__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    """Admin view for points transactions."""
    list_display = ('user', 'type', 'points', 'description', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

# Add points field to User admin
class UserAdmin(admin.ModelAdmin):
    """Admin view for users."""
    list_display = ('username', 'telegram_id', 'points', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('username', 'telegram_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
