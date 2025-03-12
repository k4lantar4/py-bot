#!/usr/bin/env python3
"""
V2Ray Account Management Telegram Bot

This module implements a Telegram bot for managing V2Ray accounts,
with features for account creation, renewal, payment processing,
and user management.
"""

import os
import sys
import logging
import json
from typing import Dict, Any, List, Optional

from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("telegram_bot")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import handlers
from handlers import (
    start,
    language,
    accounts,
    payments,
    admin,
    support,
    navigation,
    profile,
)

# Import utilities
from utils.i18n import setup_i18n, get_text
from utils.database import setup_database
from utils.config import load_config

def main() -> None:
    """Start the bot."""
    # Load configuration
    config = load_config()
    
    # Set up database
    setup_database()
    
    # Set up internationalization
    setup_i18n()
    
    # Get bot token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
        sys.exit(1)
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add handlers
    
    # Start command handler
    application.add_handler(CommandHandler("start", start.start_command))
    
    # Help command handler
    application.add_handler(CommandHandler("help", start.help_command))
    
    # Language selection handler
    application.add_handler(language.get_language_handler())
    
    # Account management handlers
    application.add_handler(accounts.get_accounts_handler())
    
    # Payment handlers
    application.add_handler(payments.get_payment_handler())
    
    # Admin handlers
    application.add_handler(admin.get_admin_handler())
    
    # Support handlers
    application.add_handler(support.get_support_handler())
    
    # Profile handlers
    application.add_handler(profile.get_profile_handler())
    
    # Navigation handlers
    application.add_handler(CallbackQueryHandler(navigation.handle_navigation))
    
    # Unknown command handler
    application.add_handler(MessageHandler(filters.COMMAND, start.unknown_command))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    if webhook_url:
        # Use webhook
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path=token,
            webhook_url=f"{webhook_url}/{token}"
        )
    else:
        # Use polling (for development)
        application.run_polling()


async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Send error message to the user
    if update and update.effective_chat:
        user_id = update.effective_chat.id
        language_code = "en"  # Default to English
        
        # Try to get user's language preference
        try:
            from utils.database import get_user_language
            language_code = get_user_language(user_id) or language_code
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
        
        error_message = get_text("error_occurred", language_code)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_message,
            parse_mode=ParseMode.MARKDOWN
        )


if __name__ == "__main__":
    main() 