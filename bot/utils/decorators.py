"""
Decorators for the Telegram bot.

This module provides decorators for common bot functionality.
"""

import logging
import functools
import os
from typing import Callable, Any, Optional, List

from telegram import Update
from telegram.ext import ContextTypes

from utils.database import get_user
from utils.i18n import get_text

logger = logging.getLogger(__name__)

# Get admin user IDs from environment variable
ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS", "[]")
try:
    ADMIN_USER_IDS = eval(ADMIN_USER_IDS)
    if not isinstance(ADMIN_USER_IDS, list):
        ADMIN_USER_IDS = []
except Exception as e:
    logger.error(f"Error parsing ADMIN_USER_IDS: {e}")
    ADMIN_USER_IDS = []

def require_user(func: Callable) -> Callable:
    """
    Decorator to check if the user exists in the database.
    
    This decorator checks if the user exists in the database.
    If not, it sends a message asking the user to register.
    
    Args:
        func: The handler function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any) -> Any:
        user_id = update.effective_user.id
        user = get_user(user_id)
        
        if not user:
            # User not found
            await update.effective_message.reply_text(
                get_text('user_not_found', 'en'),
                parse_mode='HTML'
            )
            return
        
        # User exists, proceed with handler
        return await func(update, context, *args, **kwargs)
    
    return wrapper

def require_auth(func: Callable) -> Callable:
    """
    Decorator to require user authentication before executing a handler.
    
    This decorator checks if the user exists in the database and is active.
    If not, it sends a message asking the user to register.
    
    Args:
        func: The handler function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any) -> Any:
        user_id = update.effective_user.id
        user = get_user(user_id)
        
        if not user or user.get('status') != 'active':
            # User not found or not active
            await update.effective_message.reply_text(
                get_text('auth.not_registered', user_id),
                parse_mode='HTML'
            )
            return
        
        # User is authenticated, proceed with handler
        return await func(update, context, *args, **kwargs)
    
    return wrapper

def require_admin(func: Callable) -> Callable:
    """
    Decorator to require admin privileges before executing a handler.
    
    This decorator checks if the user is in the list of admin user IDs.
    If not, it sends a message indicating that the command is only available to admins.
    
    Args:
        func: The handler function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any) -> Any:
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_USER_IDS:
            # User is not an admin
            await update.effective_message.reply_text(
                get_text('admin.not_authorized', user_id),
                parse_mode='HTML'
            )
            return
        
        # User is an admin, proceed with handler
        return await func(update, context, *args, **kwargs)
    
    return wrapper 