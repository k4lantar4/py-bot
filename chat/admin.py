from django.contrib import admin
from .models import LiveChatSession, LiveChatMessage, LiveChatOperator, LiveChatRating

@admin.register(LiveChatSession)
class LiveChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'operator', 'status', 'priority', 'subject', 'created', 'closed_at')
    list_filter = ('status', 'priority', 'created', 'closed_at')
    search_fields = ('user__username', 'operator__username', 'subject')
    date_hierarchy = 'created'

@admin.register(LiveChatMessage)
class LiveChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'type', 'created')
    list_filter = ('type', 'created')
    search_fields = ('content', 'sender__username')
    date_hierarchy = 'created'

@admin.register(LiveChatOperator)
class LiveChatOperatorAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'max_concurrent_sessions', 'current_sessions', 'last_active')
    list_filter = ('status', 'last_active')
    search_fields = ('user__username',)

@admin.register(LiveChatRating)
class LiveChatRatingAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'operator', 'rating', 'created')
    list_filter = ('rating', 'created')
    search_fields = ('user__username', 'operator__username', 'comment')
    date_hierarchy = 'created'
