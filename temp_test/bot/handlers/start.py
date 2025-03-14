"""
Start command handler for the Telegram bot.

This module handles the /start command and provides help information.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import logging
from typing import Dict, Any, List, Optional

from utils.i18n import get_text
from utils.database import get_user_language, get_user, create_user_if_not_exists

# Configure logging
logger = logging.getLogger("telegram_bot")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    user_id = user.id
    
    # Create user if not exists
    create_user_if_not_exists(
        user_id=user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code or "en"
    )
    
    # Get user's language preference
    language_code = get_user_language(user_id)
    
    # Log the start command
    logger.info(f"User {user_id} ({user.username}) started the bot")
    
    # Check if there's a deep link parameter
    args = context.args
    if args and len(args) > 0:
        # Handle deep link
        deep_link = args[0]
        logger.info(f"Deep link detected: {deep_link}")
        
        # Handle different deep link types
        if deep_link.startswith("ref_"):
            # Referral link
            referrer_id = deep_link[4:]
            logger.info(f"Referral from user {referrer_id}")
            # TODO: Handle referral
    
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
    user_data = get_user(user_id)
    if user_data and user_data.get("is_admin", False):
        keyboard.append([
            InlineKeyboardButton(
                get_text("admin_panel", language_code),
                callback_data="admin"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send welcome message
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    user = update.effective_user
    user_id = user.id
    
    # Get user's language preference
    language_code = get_user_language(user_id)
    
    # Create help message
    help_message = get_text("help", language_code)
    
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
                get_text("back", language_code),
                callback_data="back:start"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send help message
    await update.message.reply_text(
        help_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    user = update.effective_user
    user_id = user.id
    
    # Get user's language preference
    language_code = get_user_language(user_id)
    
    # Send unknown command message
    await update.message.reply_text(
        get_text("unknown_command", language_code),
        parse_mode=ParseMode.MARKDOWN
    ) 