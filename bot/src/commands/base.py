"""
Base command handlers for the bot.
"""

from telegram import Update
from telegram.ext import ContextTypes
import emoji
from ..utils.i18n import i18n
from ..utils.decorators import auth_required

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    await update.message.reply_text(
        i18n.get_text("welcome", name=user.first_name)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    user_id = update.effective_user.id
    is_admin = user_id in context.bot_data.get("admin_users", [])
    is_authenticated = user_id in context.bot_data.get("user_sessions", {})
    
    help_text = i18n.get_text("help.title")
    
    # Basic commands
    help_text += i18n.get_text("help.basic.start") + "\n"
    help_text += i18n.get_text("help.basic.help") + "\n\n"
    
    # Authentication commands
    if is_authenticated:
        help_text += i18n.get_text("help.auth.logout") + "\n"
        help_text += i18n.get_text("help.auth.profile") + "\n"
    else:
        help_text += i18n.get_text("help.auth.login") + "\n"
    
    # User commands (require authentication)
    if is_authenticated:
        help_text += "\n"
        help_text += i18n.get_text("help.user.services") + "\n"
        help_text += i18n.get_text("help.user.orders") + "\n"
        help_text += i18n.get_text("help.user.clients") + "\n"
        help_text += i18n.get_text("help.user.status") + "\n"
    
    # Admin commands
    if is_admin:
        help_text += i18n.get_text("help.admin.title")
        help_text += i18n.get_text("help.admin.users") + "\n"
        help_text += i18n.get_text("help.admin.servers") + "\n"
        help_text += i18n.get_text("help.admin.locations") + "\n"
        help_text += i18n.get_text("help.admin.stats")
    
    await update.message.reply_text(help_text) 