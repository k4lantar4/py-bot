"""
Profile management handlers for the Telegram bot.

This module provides handlers for user profile management, including
viewing and updating profile information.
"""

import logging
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
)

from utils.database import get_user, update_user
from utils.i18n import get_text, get_user_language
from utils.decorators import require_user

# Configure logging
logger = logging.getLogger("telegram_bot")

# Conversation states
PROFILE_MENU, EDIT_NAME, EDIT_EMAIL, EDIT_PHONE = range(4)

# Callback data
PROFILE_CB = "profile"
EDIT_NAME_CB = "edit_name"
EDIT_EMAIL_CB = "edit_email"
EDIT_PHONE_CB = "edit_phone"
BACK_TO_MENU_CB = "back_to_menu"

@require_user
async def profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the profile menu."""
    user_id = update.effective_user.id
    language_code = get_user_language(user_id)
    
    user = get_user(user_id)
    if not user:
        await update.effective_message.reply_text(
            get_text("user_not_found", language_code)
        )
        return ConversationHandler.END
    
    # Get user information
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    username = user.get("username", "")
    balance = user.get("balance", 0)
    
    # Format profile information
    profile_text = get_text("profile_info", language_code).format(
        user_id=user_id,
        name=f"{first_name} {last_name}".strip(),
        username=f"@{username}" if username else get_text("not_set", language_code),
        balance=balance
    )
    
    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("edit_name", language_code),
                callback_data=EDIT_NAME_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_menu", language_code),
                callback_data=BACK_TO_MENU_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send or edit message
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=profile_text,
            reply_markup=reply_markup
        )
    else:
        await update.effective_message.reply_text(
            text=profile_text,
            reply_markup=reply_markup
        )
    
    return PROFILE_MENU

@require_user
async def edit_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle name editing."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = get_user_language(user_id)
    
    await query.edit_message_text(
        text=get_text("edit_name_prompt", language_code),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    get_text("back", language_code),
                    callback_data=PROFILE_CB
                )
            ]
        ])
    )
    
    return EDIT_NAME

@require_user
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to the main menu."""
    query = update.callback_query
    await query.answer()
    
    # Call the main menu handler
    from handlers.navigation import main_menu
    return await main_menu(update, context)

def get_profile_handler() -> ConversationHandler:
    """Create and return the profile conversation handler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(profile_menu, pattern=f"^{PROFILE_CB}$"),
            CommandHandler("profile", profile_menu)
        ],
        states={
            PROFILE_MENU: [
                CallbackQueryHandler(edit_name_handler, pattern=f"^{EDIT_NAME_CB}$"),
                CallbackQueryHandler(back_to_menu, pattern=f"^{BACK_TO_MENU_CB}$"),
            ],
            EDIT_NAME: [
                CallbackQueryHandler(profile_menu, pattern=f"^{PROFILE_CB}$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(profile_menu, pattern="^menu$"),
        ],
        name="profile",
        persistent=False
    ) 