from django.contrib import admin
from .models import TelegramMessage, TelegramState, TelegramNotification, TelegramLog, TelegramCallback, BotCommand, BotSetting

# Register your models here.

@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'language_code', 'updated_at')
    list_filter = ('language_code',)
    search_fields = ('name', 'content')
    ordering = ('name', 'language_code')

@admin.register(TelegramState)
class TelegramStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'updated_at')
    list_filter = ('state',)
    search_fields = ('user__username', 'state')
    ordering = ('-updated_at',)

@admin.register(TelegramNotification)
class TelegramNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'status', 'created_at', 'sent_at')
    list_filter = ('type', 'status')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)
    actions = ['mark_as_sent', 'mark_as_pending']
    
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='sent', sent_at=timezone.now())
    mark_as_sent.short_description = "Mark selected notifications as sent"
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending', sent_at=None)
    mark_as_pending.short_description = "Mark selected notifications as pending"

@admin.register(TelegramLog)
class TelegramLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'message', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)

@admin.register(TelegramCallback)
class TelegramCallbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'callback_data', 'expires_at', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'callback_data')
    ordering = ('-created_at',)

@admin.register(BotCommand)
class BotCommandAdmin(admin.ModelAdmin):
    list_display = ('command', 'description', 'is_active', 'is_admin_only', 'updated_at')
    list_filter = ('is_active', 'is_admin_only')
    search_fields = ('command', 'description', 'handler_function')
    ordering = ('command',)

@admin.register(BotSetting)
class BotSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_public', 'updated_at')
    list_filter = ('is_public',)
    search_fields = ('key', 'value', 'description')
    ordering = ('key',)
