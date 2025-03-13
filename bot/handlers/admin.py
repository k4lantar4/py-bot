"""
Admin panel handler for the V2Ray Telegram bot.

This module implements handlers for admin operations including:
- User management
- Server management
- Payment verification
- System settings
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
)
from telegram.constants import ParseMode

from bot.utils import (
    get_text,
    format_number,
    format_date,
)
from bot.api_client import (
    get_user_profile,
    get_all_users,
    update_user_profile,
    delete_user,
    reset_user_password,
    get_all_servers,
    get_server,
    update_server,
    delete_server,
    get_pending_payments,
    verify_payment,
    reject_payment,
    get_system_settings,
    update_system_settings,
    get_payment,
    get_server_stats,
)
from bot.decorators import require_admin
from bot.constants import (
    # Conversation states
    SELECTING_FEATURE,
    SELECTING_ACTION,
    SELECTING_USER,
    SELECTING_SERVER,
    SELECTING_PAYMENT,
    ENTERING_DETAILS,
    CONFIRMING_ACTION,
    END,
    
    # Callback data patterns
    ADMIN_CB,
    USERS_CB,
    SERVERS_CB,
    PAYMENTS_CB,
    SETTINGS_CB,
    BACK_CB,
    
    # User actions
    USER_DETAILS,
    USER_BLOCK,
    USER_UNBLOCK,
    USER_DELETE,
    USER_RESET,
    USER_ADD_BALANCE,
    
    # Server actions
    SERVER_DETAILS,
    SERVER_ADD,
    SERVER_EDIT,
    SERVER_DELETE,
    SERVER_SYNC,
    
    # Payment actions
    PAYMENT_DETAILS,
    PAYMENT_VERIFY,
    PAYMENT_REJECT,
    
    # Settings actions
    SETTINGS_EDIT,
    SETTINGS_SAVE,
)
from bot.handlers.start import start, back_to_main

logger = logging.getLogger(__name__)

@require_admin
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the admin menu."""
    query = update.callback_query
    if query:
        await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Get statistics
    users_count = len(get_all_users())
    servers_count = len(get_all_servers())
    pending_payments = len(get_pending_payments())
    
    message = get_text("admin_menu_info", language_code).format(
        users=users_count,
        servers=servers_count,
        pending_payments=pending_payments
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("manage_users", language_code),
                callback_data=USERS_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("manage_servers", language_code),
                callback_data=SERVERS_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("verify_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("system_settings", language_code),
                callback_data=SETTINGS_CB
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_main", language_code),
                callback_data=BACK_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    return SELECTING_ACTION

@require_admin
async def user_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of users."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Get all users
    users = get_all_users()
    
    if not users:
        message = get_text("no_users", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_admin", language_code),
                    callback_data=ADMIN_CB
                )
            ]
        ]
    else:
        message = get_text("user_list_header", language_code) + "\n\n"
        keyboard = []
        
        for user in users:
            # Format user status
            status_emoji = "🟢" if user.get("is_active", True) else "🔴"
            username = user.get("username", "")
            user_id = user.get("id", "")
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_emoji} {username} ({user_id})",
                    callback_data=f"{USER_DETAILS}:{user_id}"
                )
            ])
    
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_admin", language_code),
            callback_data=ADMIN_CB
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_USER

@require_admin
async def user_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user details and management options."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = query.data.split(":")[-1]
    
    # Get user details
    user = get_user_profile(user_id)
    
    if not user:
        message = get_text("user_not_found", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_users", language_code),
                    callback_data=USERS_CB
                )
            ],
        ]
    else:
        # Format user details
        username = user.get("username", "")
        name = user.get("name", "")
        email = user.get("email", "")
        phone = user.get("phone", "")
        is_active = user.get("is_active", True)
        is_admin = user.get("is_admin", False)
        accounts_count = len(user.get("accounts", []))
        wallet_balance = user.get("wallet_balance", 0)
        created_at = user.get("created_at", "")
        
        message = get_text("user_details_template", language_code).format(
            id=user_id,
            username=username,
            name=name or get_text("not_provided", language_code),
            email=email or get_text("not_provided", language_code),
            phone=phone or get_text("not_provided", language_code),
            status=get_text("active", language_code) if is_active else get_text("blocked", language_code),
            admin=get_text("yes", language_code) if is_admin else get_text("no", language_code),
            accounts=accounts_count,
            balance=format_number(wallet_balance, language_code),
            created_at=format_date(created_at, language_code)
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("block_user", language_code) if is_active else get_text("unblock_user", language_code),
                    callback_data=f"{USER_BLOCK if is_active else USER_UNBLOCK}:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("add_balance", language_code),
                    callback_data=f"{USER_ADD_BALANCE}:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("delete_user", language_code),
                    callback_data=f"{USER_DELETE}:{user_id}"
                ),
                InlineKeyboardButton(
                    get_text("reset_password", language_code),
                    callback_data=f"{USER_RESET}:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_users", language_code),
                    callback_data=USERS_CB
                )
            ],
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_USER

@require_admin
async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Block a user."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = query.data.split(":")[-1]
    
    # Update user status
    try:
        updated_user = update_user_profile(user_id, {"is_active": False})
        
        if updated_user:
            message = get_text("user_blocked", language_code).format(id=user_id)
        else:
            message = get_text("user_block_failed", language_code)
    except Exception as e:
        logger.error(f"Error blocking user: {e}")
        message = get_text("user_block_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_user", language_code),
                callback_data=f"{USER_DETAILS}:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_users", language_code),
                callback_data=USERS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_USER

@require_admin
async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Unblock a user."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = query.data.split(":")[-1]
    
    # Update user status
    try:
        updated_user = update_user_profile(user_id, {"is_active": True})
        
        if updated_user:
            message = get_text("user_unblocked", language_code).format(id=user_id)
        else:
            message = get_text("user_unblock_failed", language_code)
    except Exception as e:
        logger.error(f"Error unblocking user: {e}")
        message = get_text("user_unblock_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_user", language_code),
                callback_data=f"{USER_DETAILS}:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_users", language_code),
                callback_data=USERS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_USER

@require_admin
async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete a user."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = query.data.split(":")[-1]
    
    # Store user ID for confirmation
    context.user_data["delete_user_id"] = user_id
    
    message = get_text("confirm_delete_user", language_code).format(id=user_id)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("confirm_delete", language_code),
                callback_data=f"confirm_delete_user:{user_id}"
            ),
            InlineKeyboardButton(
                get_text("cancel", language_code),
                callback_data=f"{USER_DETAILS}:{user_id}"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CONFIRMING_ACTION

@require_admin
async def confirm_delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm and process user deletion."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = query.data.split(":")[-1]
    
    # Check if this is the same user we wanted to delete
    stored_user_id = context.user_data.get("delete_user_id")
    if stored_user_id != user_id:
        message = get_text("delete_user_mismatch", language_code)
    else:
        # Delete the user
        try:
            deleted = delete_user(user_id)
            
            if deleted:
                message = get_text("user_deleted", language_code).format(id=user_id)
            else:
                message = get_text("user_delete_failed", language_code)
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            message = get_text("user_delete_error", language_code)
        
        # Clear stored user ID
        if "delete_user_id" in context.user_data:
            del context.user_data["delete_user_id"]
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_users", language_code),
                callback_data=USERS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_USER

@require_admin
async def reset_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Reset a user's password."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = query.data.split(":")[-1]
    
    # Reset password
    try:
        result = reset_user_password(user_id)
        
        if result and "password" in result:
            new_password = result["password"]
            message = get_text("password_reset_success", language_code).format(
                id=user_id,
                password=new_password
            )
        else:
            message = get_text("password_reset_failed", language_code)
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        message = get_text("password_reset_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_user", language_code),
                callback_data=f"{USER_DETAILS}:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_users", language_code),
                callback_data=USERS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_USER

@require_admin
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Add balance to a user's wallet."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = query.data.split(":")[-1]
    
    # Store user ID for later
    context.user_data["add_balance_user_id"] = user_id
    
    message = get_text("add_balance_prompt", language_code).format(id=user_id)
    
    await query.edit_message_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return ENTERING_DETAILS

@require_admin
async def process_add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the balance amount input."""
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get the target user ID
    target_user_id = context.user_data.get("add_balance_user_id")
    
    if not target_user_id:
        await update.message.reply_text(
            get_text("add_balance_error", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_USER
    
    # Get the amount
    try:
        amount = float(update.message.text.strip())
        
        if amount <= 0:
            await update.message.reply_text(
                get_text("invalid_amount", language_code),
                parse_mode=ParseMode.MARKDOWN
            )
            return ENTERING_DETAILS
        
        # Add balance to user's wallet
        from bot.api_client import add_user_balance
        
        result = add_user_balance(target_user_id, amount)
        
        if result:
            new_balance = result.get("wallet_balance", 0)
            message = get_text("balance_added", language_code).format(
                amount=format_number(amount, language_code),
                id=target_user_id,
                balance=format_number(new_balance, language_code)
            )
        else:
            message = get_text("add_balance_failed", language_code)
    except ValueError:
        await update.message.reply_text(
            get_text("invalid_amount", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return ENTERING_DETAILS
    except Exception as e:
        logger.error(f"Error adding balance: {e}")
        message = get_text("add_balance_error", language_code)
    
    # Clear stored user ID
    if "add_balance_user_id" in context.user_data:
        del context.user_data["add_balance_user_id"]
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_user", language_code),
                callback_data=f"{USER_DETAILS}:{target_user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_users", language_code),
                callback_data=USERS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_USER

@require_admin
async def server_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of servers."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Get all servers
    servers = get_all_servers()
    
    if not servers:
        message = get_text("no_servers", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("add_server", language_code),
                    callback_data=SERVER_ADD
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_admin", language_code),
                    callback_data=ADMIN_CB
                )
            ]
        ]
    else:
        message = get_text("server_list_header", language_code) + "\n\n"
        keyboard = []
        
        for server in servers:
            # Get server status
            server_id = server.get("id", "")
            server_name = server.get("name", "")
            server_status = server.get("status", "offline")
            
            # Format server status
            status_emoji = "🟢" if server_status == "online" else "🔴"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_emoji} {server_name}",
                    callback_data=f"{SERVER_DETAILS}:{server_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(
                get_text("add_server", language_code),
                callback_data=SERVER_ADD
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_admin", language_code),
            callback_data=ADMIN_CB
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_SERVER

def get_admin_handlers() -> List[ConversationHandler]:
    """Return the handlers for admin functionality."""
    # Admin conversation handler
    admin_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                admin_menu, pattern=f"^{ADMIN_CB}$"
            )
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(user_list, pattern=f"^{USERS_CB}$"),
                CallbackQueryHandler(server_list, pattern=f"^{SERVERS_CB}$"),
                CallbackQueryHandler(payment_list, pattern=f"^{PAYMENTS_CB}$"),
                CallbackQueryHandler(system_settings, pattern=f"^{SETTINGS_CB}$"),
            ],
            SELECTING_USER: [
                CallbackQueryHandler(user_details, pattern=f"^{USER_DETAILS}:"),
                CallbackQueryHandler(block_user, pattern=f"^{USER_BLOCK}:"),
                CallbackQueryHandler(unblock_user, pattern=f"^{USER_UNBLOCK}:"),
                CallbackQueryHandler(delete_user, pattern=f"^{USER_DELETE}:"),
                CallbackQueryHandler(reset_password, pattern=f"^{USER_RESET}:"),
                CallbackQueryHandler(add_balance, pattern=f"^{USER_ADD_BALANCE}:"),
                CallbackQueryHandler(confirm_delete_user, pattern=f"^confirm_delete_user:"),
                CallbackQueryHandler(user_list, pattern=f"^{USERS_CB}$"),
            ],
            SELECTING_SERVER: [
                CallbackQueryHandler(server_details, pattern=f"^{SERVER_DETAILS}:"),
                CallbackQueryHandler(add_server, pattern=f"^{SERVER_ADD}$"),
                CallbackQueryHandler(edit_server, pattern=f"^{SERVER_EDIT}:"),
                CallbackQueryHandler(delete_server, pattern=f"^{SERVER_DELETE}:"),
                CallbackQueryHandler(sync_server, pattern=f"^{SERVER_SYNC}:"),
                CallbackQueryHandler(server_list, pattern=f"^{SERVERS_CB}$"),
            ],
            SELECTING_PAYMENT: [
                CallbackQueryHandler(payment_details, pattern=f"^{PAYMENT_DETAILS}:"),
                CallbackQueryHandler(verify_payment, pattern=f"^{PAYMENT_VERIFY}:"),
                CallbackQueryHandler(reject_payment, pattern=f"^{PAYMENT_REJECT}:"),
                CallbackQueryHandler(payment_list, pattern=f"^{PAYMENTS_CB}$"),
            ],
            ENTERING_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_add_balance),
                CallbackQueryHandler(admin_menu, pattern=f"^{ADMIN_CB}$"),
            ],
            CONFIRMING_ACTION: [
                CallbackQueryHandler(confirm_delete_user, pattern=f"^confirm_delete_user:"),
                CallbackQueryHandler(user_details, pattern=f"^{USER_DETAILS}:"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(back_to_main, pattern=f"^{BACK_CB}$"),
            CommandHandler("start", start)
        ],
        map_to_parent={
            END: SELECTING_FEATURE,
        },
        name="admin_conversation",
        persistent=True
    )
    
    return [admin_handler] 