"""
Callback query handlers for the bot.
"""

from telegram import Update
from telegram.ext import ContextTypes
from ..commands.admin import users_command

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press
    
    # Parse callback data
    data = query.data.split(":")
    if len(data) != 2:
        return
    
    action, value = data
    
    if action == "users_page":
        try:
            page = int(value)
            context.user_data["users_page"] = page
            await users_command(update, context)
        except ValueError:
            pass 