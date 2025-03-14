"""
Navigation handler for the Telegram bot.

This module handles navigation between different sections of the bot.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import logging
from typing import Dict, Any, List, Optional

from utils.i18n import get_text
from utils.database import get_user_language

# Import handlers
from handlers import start

# Configure logging
logger = logging.getLogger("telegram_bot")


async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle navigation callbacks."""
    query = update.callback_query
    
    # Skip if the callback query is not for navigation
    if not query.data.startswith("back:"):
        return
    
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    
    # Get user's language preference
    language_code = get_user_language(user_id)
    
    # Get the target section from callback data
    # Expected format: "back:SECTION"
    callback_data = query.data
    target_section = callback_data.split(":")[1]
    
    # Handle navigation to different sections
    if target_section == "start":
        # Navigate to start menu
        await navigate_to_start(update, context, language_code)
    elif target_section == "accounts":
        # Navigate to accounts menu
        await navigate_to_accounts(update, context, language_code)
    elif target_section == "profile":
        # Navigate to profile menu
        await navigate_to_profile(update, context, language_code)
    elif target_section == "support":
        # Navigate to support menu
        await navigate_to_support(update, context, language_code)
    elif target_section == "admin":
        # Navigate to admin menu
        await navigate_to_admin(update, context, language_code)
    else:
        # Unknown section, navigate to start menu
        await navigate_to_start(update, context, language_code)


async def navigate_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE, language_code: str) -> None:
    """Navigate to the start menu."""
    query = update.callback_query
    user = update.effective_user
    
    # Create welcome message
    welcome_message = get_text("welcome", language_code).format(user.first_name)
    
    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("accounts", language_code),
                callback_data="accounts"
            ),
            InlineKeyboardButton(
                get_text("profile", language_code),
                callback_data="profile"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("support", language_code),
                callback_data="support"
            ),
            InlineKeyboardButton(
                get_text("language", language_code),
                callback_data="language"
            )
        ]
    ]
    
    # Add admin button if user is admin
    from utils.database import get_user
    user_data = get_user(user.id)
    if user_data and user_data.get("is_admin", False):
        keyboard.append([
            InlineKeyboardButton(
                get_text("admin_panel", language_code),
                callback_data="admin"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Edit message
    await query.edit_message_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def navigate_to_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE, language_code: str) -> None:
    """Navigate to the accounts menu."""
    # This will be handled by the accounts handler
    # Just trigger the accounts callback
    context.user_data["callback_query"] = update.callback_query
    context.user_data["language_code"] = language_code
    
    # Create a new callback query with the accounts callback data
    update.callback_query.data = "accounts"
    
    # Let the accounts handler handle it
    return


async def navigate_to_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, language_code: str) -> None:
    """Navigate to the profile menu."""
    # This will be handled by the profile handler
    # Just trigger the profile callback
    context.user_data["callback_query"] = update.callback_query
    context.user_data["language_code"] = language_code
    
    # Create a new callback query with the profile callback data
    update.callback_query.data = "profile"
    
    # Let the profile handler handle it
    return


async def navigate_to_support(update: Update, context: ContextTypes.DEFAULT_TYPE, language_code: str) -> None:
    """Navigate to the support menu."""
    # This will be handled by the support handler
    # Just trigger the support callback
    context.user_data["callback_query"] = update.callback_query
    context.user_data["language_code"] = language_code
    
    # Create a new callback query with the support callback data
    update.callback_query.data = "support"
    
    # Let the support handler handle it
    return


async def navigate_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, language_code: str) -> None:
    """Navigate to the admin menu."""
    # This will be handled by the admin handler
    # Just trigger the admin callback
    context.user_data["callback_query"] = update.callback_query
    context.user_data["language_code"] = language_code
    
    # Create a new callback query with the admin callback data
    update.callback_query.data = "admin"
    
    # Let the admin handler handle it
    return 