"""
Profile management handlers for the Telegram bot.

This module provides handlers for user profile management, including
viewing and updating profile information.
"""

import logging
from typing import Dict, Any, Optional, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from telegram.constants import ParseMode

from utils.database import get_user, update_user
from utils.i18n import get_text, get_user_language
from utils.decorators import require_user

from bot.api_client import (
    get_user_profile,
    update_user_profile,
    get_user_wallet_balance,
    get_user_transactions,
)
from bot.decorators import require_auth
from bot.constants import (
    # Conversation states
    SELECTING_FEATURE,
    SELECTING_ACTION,
    TYPING_NAME,
    TYPING_EMAIL,
    TYPING_PHONE,
    END,
    
    # Callback data
    PROFILE_CB,
    EDIT_PROFILE_CB,
    VIEW_PROFILE_CB,
    TRANSACTIONS_CB,
    WALLET_CB,
    BACK_CB,
    
    # Profile fields
    EDIT_NAME,
    EDIT_EMAIL,
    EDIT_PHONE,
)
from bot.handlers.start import start, back_to_main

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

@require_auth
async def profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the profile menu."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user profile
    profile = get_user_profile(user_id)
    wallet_balance = get_user_wallet_balance(user_id)
    
    message = get_text("profile_menu", language_code).format(
        balance=format_number(wallet_balance, language_code)
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("view_profile", language_code),
                callback_data=VIEW_PROFILE_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("edit_profile", language_code),
                callback_data=EDIT_PROFILE_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("transaction_history", language_code),
                callback_data=TRANSACTIONS_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_main", language_code),
                callback_data=BACK_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_ACTION

@require_auth
async def view_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the user's profile."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user profile
    profile = get_user_profile(user_id)
    
    if not profile:
        message = get_text("profile_not_found", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_profile", language_code),
                    callback_data=PROFILE_CB
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SELECTING_ACTION
    
    # Format profile
    username = profile.get("username", "")
    name = profile.get("name", "")
    email = profile.get("email", "")
    phone = profile.get("phone", "")
    created_at = profile.get("created_at", "")
    
    message = get_text("profile_details", language_code).format(
        username=username,
        name=name or get_text("not_provided", language_code),
        email=email or get_text("not_provided", language_code),
        phone=phone or get_text("not_provided", language_code),
        created_at=format_date(created_at, language_code)
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("edit_profile", language_code),
                callback_data=EDIT_PROFILE_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_profile", language_code),
                callback_data=PROFILE_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_ACTION

@require_auth
async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the edit profile menu."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user profile
    profile = get_user_profile(user_id)
    
    if not profile:
        message = get_text("profile_not_found", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_profile", language_code),
                    callback_data=PROFILE_CB
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SELECTING_ACTION
    
    # Format current profile
    name = profile.get("name", "")
    email = profile.get("email", "")
    phone = profile.get("phone", "")
    
    message = get_text("edit_profile_menu", language_code).format(
        name=name or get_text("not_provided", language_code),
        email=email or get_text("not_provided", language_code),
        phone=phone or get_text("not_provided", language_code)
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("edit_name", language_code),
                callback_data=EDIT_NAME
            )
        ],
        [
            InlineKeyboardButton(
                get_text("edit_email", language_code),
                callback_data=EDIT_EMAIL
            )
        ],
        [
            InlineKeyboardButton(
                get_text("edit_phone", language_code),
                callback_data=EDIT_PHONE
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_profile", language_code),
                callback_data=PROFILE_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_ACTION

@require_auth
async def edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle name editing."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get current name
    profile = get_user_profile(user_id)
    current_name = profile.get("name", "")
    
    message = get_text("edit_name_prompt", language_code).format(
        current=current_name or get_text("not_provided", language_code)
    )
    
    # Store the field we're editing
    context.user_data["edit_field"] = "name"
    
    await query.edit_message_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return TYPING_NAME

@require_auth
async def edit_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle email editing."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get current email
    profile = get_user_profile(user_id)
    current_email = profile.get("email", "")
    
    message = get_text("edit_email_prompt", language_code).format(
        current=current_email or get_text("not_provided", language_code)
    )
    
    # Store the field we're editing
    context.user_data["edit_field"] = "email"
    
    await query.edit_message_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return TYPING_EMAIL

@require_auth
async def edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle phone editing."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get current phone
    profile = get_user_profile(user_id)
    current_phone = profile.get("phone", "")
    
    message = get_text("edit_phone_prompt", language_code).format(
        current=current_phone or get_text("not_provided", language_code)
    )
    
    # Store the field we're editing
    context.user_data["edit_field"] = "phone"
    
    await query.edit_message_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return TYPING_PHONE

@require_auth
async def process_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the profile edit input."""
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get the field being edited
    edit_field = context.user_data.get("edit_field", "")
    
    if not edit_field:
        return await back_to_profile(update, context)
    
    # Get the new value
    new_value = update.message.text.strip()
    
    # Validate input based on field
    if edit_field == "email" and "@" not in new_value:
        await update.message.reply_text(
            get_text("invalid_email", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return TYPING_EMAIL
    
    # Update the profile
    try:
        updated_profile = update_user_profile(user_id, {edit_field: new_value})
        
        if updated_profile:
            message = get_text("profile_updated", language_code).format(
                field=get_text(f"field_{edit_field}", language_code),
                value=new_value
            )
        else:
            message = get_text("profile_update_failed", language_code)
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        message = get_text("profile_update_error", language_code)
    
    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("continue_editing", language_code),
                callback_data=EDIT_PROFILE_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_profile", language_code),
                callback_data=PROFILE_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Clear the edit field
    if "edit_field" in context.user_data:
        del context.user_data["edit_field"]
    
    return SELECTING_ACTION

@require_auth
async def transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the user's transaction history."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get transactions, limit to 10 most recent
    transactions = get_user_transactions(user_id, limit=10)
    
    if not transactions:
        message = get_text("no_transactions", language_code)
    else:
        message = get_text("transaction_history_header", language_code) + "\n\n"
        
        for tx in transactions:
            tx_id = tx.get("id", "")
            tx_type = tx.get("transaction_type", "")
            tx_amount = tx.get("amount", 0)
            tx_date = tx.get("created_at", "")
            tx_status = tx.get("status", "")
            
            # Format the transaction entry
            message += "💰 *" + get_text(f"transaction_type_{tx_type}", language_code) + "*\n"
            message += f"📅 {format_date(tx_date, language_code)}\n"
            
            # Format amount with color indication (positive/negative)
            if tx_amount > 0:
                message += f"➕ {format_number(tx_amount, language_code)}\n"
            else:
                message += f"➖ {format_number(abs(tx_amount), language_code)}\n"
            
            message += f"🆔 `{tx_id}`\n"
            message += f"📊 {get_text(f'status_{tx_status}', language_code)}\n\n"
    
    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_profile", language_code),
                callback_data=PROFILE_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_ACTION

@require_auth
async def back_to_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to the profile menu."""
    query = update.callback_query
    if query:
        await query.answer()
        await profile_menu(update, context)
    else:
        # Fallback for message handlers
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_profile", context.user_data.get("language", "en")),
                    callback_data=PROFILE_CB
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=get_text("back_to_profile_message", context.user_data.get("language", "en")),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    return SELECTING_ACTION

def get_profile_handlers() -> List[ConversationHandler]:
    """Return the handlers for profile functionality."""
    # Profile conversation handler
    profile_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                profile_menu, pattern=f"^{PROFILE_CB}$"
            )
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(view_profile, pattern=f"^{VIEW_PROFILE_CB}$"),
                CallbackQueryHandler(edit_profile, pattern=f"^{EDIT_PROFILE_CB}$"),
                CallbackQueryHandler(transaction_history, pattern=f"^{TRANSACTIONS_CB}$"),
                CallbackQueryHandler(edit_name, pattern=f"^{EDIT_NAME}$"),
                CallbackQueryHandler(edit_email, pattern=f"^{EDIT_EMAIL}$"),
                CallbackQueryHandler(edit_phone, pattern=f"^{EDIT_PHONE}$"),
            ],
            TYPING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_edit)
            ],
            TYPING_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_edit)
            ],
            TYPING_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_edit)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(back_to_profile, pattern=f"^{PROFILE_CB}$"),
            CallbackQueryHandler(back_to_main, pattern=f"^{BACK_CB}$"),
            CommandHandler("start", start)
        ],
        map_to_parent={
            END: SELECTING_FEATURE,
        },
        name="profile_conversation",
        persistent=True
    )
    
    return [profile_handler] 