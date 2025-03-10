"""
Decorator utilities for command handlers.
"""

from functools import wraps
from typing import Callable, Any
from telegram import Update
from telegram.ext import ContextTypes
import emoji
from ..config.settings import settings

def admin_required(func: Callable) -> Callable:
    """
    Decorator to require admin privileges for a command.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user_id = update.effective_user.id
        if user_id not in settings.ADMIN_USER_IDS:
            await update.message.reply_text(
                f"{emoji.emojize(':prohibited:')} Sorry, this command is only available to administrators."
            )
            return
        return await func(update, context)
    return wrapper

def auth_required(func: Callable) -> Callable:
    """
    Decorator to require authentication for a command.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user_id = update.effective_user.id
        if "user_sessions" not in context.bot_data or user_id not in context.bot_data["user_sessions"]:
            await update.message.reply_text(
                f"{emoji.emojize(':locked:')} You need to log in first. Use /login to authenticate."
            )
            return
        return await func(update, context)
    return wrapper 