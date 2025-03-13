from django.contrib import admin
from .models import LiveChatSession, LiveChatMessage, LiveChatOperator, LiveChatRating

@admin.register(LiveChatSession)
class LiveChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'operator', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('user__username', 'operator__username', 'subject')
    readonly_fields = ('created_at', 'updated_at', 'closed_at')
    ordering = ('-created_at',)

@admin.register(LiveChatMessage)
class LiveChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'message_type', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('session__id', 'sender__username', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(LiveChatOperator)
class LiveChatOperatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'current_sessions', 'max_sessions', 'last_active')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at', 'last_active')
    ordering = ('-created_at',)

@admin.register(LiveChatRating)
class LiveChatRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'operator', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('session__id', 'user__username', 'operator__username', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',) 