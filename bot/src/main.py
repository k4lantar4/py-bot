"""
Main entry point for the Telegram bot.
"""

import logging
import sys
from pathlib import Path
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.commands.base import start_command, help_command
from src.commands.auth import (
    login_command,
    logout_command,
    profile_command,
    handle_login_flow,
)
from src.commands.user import (
    services_command,
    orders_command,
    clients_command,
)
from src.commands.admin import (
    users_command,
    servers_command,
    locations_command,
    stats_command,
)
from src.handlers.callbacks import handle_callback_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("telegram_bot")

async def error_handler(update, context):
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Basic commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Authentication commands
    application.add_handler(CommandHandler("login", login_command))
    application.add_handler(CommandHandler("logout", logout_command))
    application.add_handler(CommandHandler("profile", profile_command))
    
    # User commands
    application.add_handler(CommandHandler("services", services_command))
    application.add_handler(CommandHandler("orders", orders_command))
    application.add_handler(CommandHandler("clients", clients_command))
    
    # Admin commands
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("servers", servers_command))
    application.add_handler(CommandHandler("locations", locations_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Message handlers
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_login_flow
        )
    )
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main() 