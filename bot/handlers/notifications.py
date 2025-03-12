"""
Notification settings handler for the V2Ray Telegram bot.

This module implements handlers for managing user notification preferences including:
- Account expiry notifications
- Traffic usage alerts
- Payment reminders
- System status updates
"""

import logging
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

from utils.i18n import get_text
from utils.database import get_user, update_user
from utils.decorators import require_auth

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_ACTION = 0

# Callback data patterns
NOTIFICATIONS_CB = "notifications"
TOGGLE_EXPIRY = f"{NOTIFICATIONS_CB}_expiry"
TOGGLE_TRAFFIC = f"{NOTIFICATIONS_CB}_traffic"
TOGGLE_PAYMENTS = f"{NOTIFICATIONS_CB}_payments"
TOGGLE_SYSTEM = f"{NOTIFICATIONS_CB}_system"

@require_auth
async def notifications_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show notification settings menu."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user notification settings
    user = get_user(user_id)
    settings = user.get("notification_settings", {
        "expiry": True,
        "traffic": True,
        "payments": True,
        "system": True
    })
    
    text = get_text("notification_settings_info", language_code).format(
        expiry="✓" if settings["expiry"] else "✗",
        traffic="✓" if settings["traffic"] else "✗",
        payments="✓" if settings["payments"] else "✗",
        system="✓" if settings["system"] else "✗"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{get_text('expiry_notifications', language_code)} {'✓' if settings['expiry'] else '✗'}",
                callback_data=TOGGLE_EXPIRY
            )
        ],
        [
            InlineKeyboardButton(
                f"{get_text('traffic_notifications', language_code)} {'✓' if settings['traffic'] else '✗'}",
                callback_data=TOGGLE_TRAFFIC
            )
        ],
        [
            InlineKeyboardButton(
                f"{get_text('payment_notifications', language_code)} {'✓' if settings['payments'] else '✗'}",
                callback_data=TOGGLE_PAYMENTS
            )
        ],
        [
            InlineKeyboardButton(
                f"{get_text('system_notifications', language_code)} {'✓' if settings['system'] else '✗'}",
                callback_data=TOGGLE_SYSTEM
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_settings", language_code),
                callback_data="profile_settings"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

async def toggle_notification(update: Update, context: ContextTypes.DEFAULT_TYPE, setting_type: str) -> int:
    """Toggle a specific notification setting."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    # Get current settings or set defaults
    settings = user.get("notification_settings", {
        "expiry": True,
        "traffic": True,
        "payments": True,
        "system": True
    })
    
    # Toggle the specified setting
    settings[setting_type] = not settings[setting_type]
    
    # Update user settings in database
    update_user(user_id, {"notification_settings": settings})
    
    # Return to notifications menu
    return await notifications_menu(update, context)

async def toggle_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Toggle expiry notifications."""
    return await toggle_notification(update, context, "expiry")

async def toggle_traffic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Toggle traffic notifications."""
    return await toggle_notification(update, context, "traffic")

async def toggle_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Toggle payment notifications."""
    return await toggle_notification(update, context, "payments")

async def toggle_system(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Toggle system notifications."""
    return await toggle_notification(update, context, "system")

def get_notifications_handler() -> ConversationHandler:
    """Create and return the notifications conversation handler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(notifications_menu, pattern=f"^{NOTIFICATIONS_CB}$")
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(toggle_expiry, pattern=f"^{TOGGLE_EXPIRY}$"),
                CallbackQueryHandler(toggle_traffic, pattern=f"^{TOGGLE_TRAFFIC}$"),
                CallbackQueryHandler(toggle_payments, pattern=f"^{TOGGLE_PAYMENTS}$"),
                CallbackQueryHandler(toggle_system, pattern=f"^{TOGGLE_SYSTEM}$"),
                CallbackQueryHandler(notifications_menu, pattern=f"^{NOTIFICATIONS_CB}$"),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(notifications_menu, pattern="^profile_settings$")
        ],
        name="notifications",
        persistent=True
    ) 