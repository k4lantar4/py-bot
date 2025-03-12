"""
Admin panel handler for the V2Ray Telegram bot.

This module implements handlers for admin operations including:
- User management
- Server management
- Payment verification
- System settings
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

from utils.i18n import get_text, format_number, format_date
from utils.database import (
    get_user,
    get_all_users,
    update_user,
    delete_user as delete_user_db,
    reset_user_password,
    get_all_servers,
    get_server_details,
    update_server,
    delete_server as delete_server_db,
    get_pending_payments,
    verify_payment,
    reject_payment as reject_payment_db,
    get_system_settings,
    update_system_settings,
    get_payment_details,
)
from utils.xui_api import XUIClient
from utils.decorators import require_admin

logger = logging.getLogger(__name__)

# Conversation states
(
    SELECTING_ACTION,
    SELECTING_USER,
    SELECTING_SERVER,
    SELECTING_PAYMENT,
    ENTERING_DETAILS,
    CONFIRMING_ACTION,
) = range(6)

# Callback data patterns
ADMIN_CB = "admin"
USERS = f"{ADMIN_CB}_users"
SERVERS = f"{ADMIN_CB}_servers"
PAYMENTS = f"{ADMIN_CB}_payments"
SETTINGS = f"{ADMIN_CB}_settings"

USER_DETAILS = f"{USERS}_details"
USER_BLOCK = f"{USERS}_block"
USER_UNBLOCK = f"{USERS}_unblock"
USER_DELETE = f"{USERS}_delete"
USER_RESET = f"{USERS}_reset"

SERVER_DETAILS = f"{SERVERS}_details"
SERVER_ADD = f"{SERVERS}_add"
SERVER_EDIT = f"{SERVERS}_edit"
SERVER_DELETE = f"{SERVERS}_delete"
SERVER_SYNC = f"{SERVERS}_sync"

PAYMENT_DETAILS = f"{PAYMENTS}_details"
PAYMENT_VERIFY = f"{PAYMENTS}_verify"
PAYMENT_REJECT = f"{PAYMENTS}_reject"

SETTINGS_EDIT = f"{SETTINGS}_edit"
SETTINGS_SAVE = f"{SETTINGS}_save"

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
    
    text = get_text("admin_menu_info", language_code).format(
        users=users_count,
        servers=servers_count,
        pending_payments=pending_payments
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("manage_users", language_code),
                callback_data=USERS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("manage_servers", language_code),
                callback_data=SERVERS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("verify_payments", language_code),
                callback_data=PAYMENTS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("system_settings", language_code),
                callback_data=SETTINGS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_menu", language_code),
                callback_data="menu"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)
    
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
        text = get_text("no_users", language_code)
    else:
        text = get_text("user_list_header", language_code) + "\n\n"
        keyboard = []
        
        for user in users:
            # Format user status
            status_emoji = "🟢" if user["is_active"] else "🔴"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_emoji} {user['username']} ({user['id']})",
                    callback_data=f"{USER_DETAILS}_{user['id']}"
                )
            ])
    
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_admin", language_code),
            callback_data=ADMIN_CB
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_USER

@require_admin
async def user_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user details and management options."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = int(query.data.split("_")[-1])
    
    # Get user details
    user = get_user(user_id)
    if not user:
        text = get_text("user_not_found", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_users", language_code),
                    callback_data=USERS
                )
            ],
        ]
    else:
        text = get_text("user_details_template", language_code).format(
            id=user["id"],
            username=user["username"],
            name=user.get("name", "N/A"),
            email=user.get("email", "N/A"),
            phone=user.get("phone", "N/A"),
            status="Active" if user["is_active"] else "Blocked",
            accounts=len(user.get("accounts", [])),
            balance=format_number(user.get("wallet_balance", 0), language_code),
            created_at=format_date(user["created_at"], language_code)
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("block_user" if user["is_active"] else "unblock_user", language_code),
                    callback_data=f"{USER_BLOCK if user['is_active'] else USER_UNBLOCK}_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("delete_user", language_code),
                    callback_data=f"{USER_DELETE}_{user_id}"
                ),
                InlineKeyboardButton(
                    get_text("reset_password", language_code),
                    callback_data=f"{USER_RESET}_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_users", language_code),
                    callback_data=USERS
                )
            ],
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
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
        text = get_text("no_servers", language_code)
    else:
        text = get_text("server_list_header", language_code) + "\n\n"
        keyboard = []
        
        for server in servers:
            # Format server status
            status_emoji = "🟢" if server["is_active"] else "🔴"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_emoji} {server['name']}",
                    callback_data=f"{SERVER_DETAILS}_{server['id']}"
                )
            ])
    
    # Add server management buttons
    keyboard.extend([
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
        ],
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_SERVER

@require_admin
async def server_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show server details and management options."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    server_id = int(query.data.split("_")[-1])
    
    # Get server details
    server = get_server_details(server_id)
    if not server:
        text = get_text("server_not_found", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_servers", language_code),
                    callback_data=SERVERS
                )
            ],
        ]
    else:
        text = get_text("server_details_template", language_code).format(
            id=server["id"],
            name=server["name"],
            host=server["host"],
            port=server["port"],
            status="Active" if server["is_active"] else "Inactive",
            panel_url=server["panel_url"],
            inbounds=server.get("inbounds_count", 0),
            clients=server.get("clients_count", 0),
            created_at=format_date(server["created_at"], language_code)
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("edit_server", language_code),
                    callback_data=f"{SERVER_EDIT}_{server_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("delete_server", language_code),
                    callback_data=f"{SERVER_DELETE}_{server_id}"
                ),
                InlineKeyboardButton(
                    get_text("sync_server", language_code),
                    callback_data=f"{SERVER_SYNC}_{server_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_servers", language_code),
                    callback_data=SERVERS
                )
            ],
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_SERVER

@require_admin
async def payment_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of pending payments."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Get pending payments
    payments = get_pending_payments()
    
    if not payments:
        text = get_text("no_pending_payments", language_code)
    else:
        text = get_text("payment_list_header", language_code) + "\n\n"
        keyboard = []
        
        for payment in payments:
            keyboard.append([
                InlineKeyboardButton(
                    f"💰 {payment['user_name']} - {format_number(payment['amount'], language_code)}",
                    callback_data=f"{PAYMENT_DETAILS}_{payment['id']}"
                )
            ])
    
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_admin", language_code),
            callback_data=ADMIN_CB
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_PAYMENT

@require_admin
async def payment_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show payment details and verification options."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    payment_id = int(query.data.split("_")[-1])
    
    # Get payment details
    payment = get_payment_details(payment_id)
    if not payment:
        text = get_text("payment_not_found", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_payments", language_code),
                    callback_data=PAYMENTS
                )
            ],
        ]
    else:
        text = get_text("payment_details_template", language_code).format(
            id=payment["id"],
            user_name=payment["user_name"],
            amount=format_number(payment["amount"], language_code),
            method=get_text(f"payment_method_{payment['method']}", language_code),
            status=get_text(f"payment_status_{payment['status']}", language_code),
            created_at=format_date(payment["created_at"], language_code)
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("verify_payment", language_code),
                    callback_data=f"{PAYMENT_VERIFY}_{payment_id}"
                ),
                InlineKeyboardButton(
                    get_text("reject_payment", language_code),
                    callback_data=f"{PAYMENT_REJECT}_{payment_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_payments", language_code),
                    callback_data=PAYMENTS
                )
            ],
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_PAYMENT

@require_admin
async def system_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show system settings."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Get system settings
    settings = get_system_settings()
    
    text = get_text("system_settings_template", language_code).format(
        maintenance_mode="✓" if settings.get("maintenance_mode", False) else "✗",
        registration_enabled="✓" if settings.get("registration_enabled", True) else "✗",
        auto_renewal="✓" if settings.get("auto_renewal", False) else "✗",
        notification_delay=settings.get("notification_delay", 3),
        traffic_threshold=settings.get("traffic_threshold", 80)
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("edit_settings", language_code),
                callback_data=SETTINGS_EDIT
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_admin", language_code),
                callback_data=ADMIN_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

@require_admin
async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Block a user."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = int(query.data.split("_")[-1])
    
    try:
        # Update user status
        update_user(user_id, {"is_active": False})
        text = get_text("user_blocked", language_code)
    except Exception as e:
        logger.error(f"Error blocking user {user_id}: {e}")
        text = get_text("block_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_user", language_code),
                callback_data=f"{USER_DETAILS}_{user_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_USER

@require_admin
async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Unblock a user."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = int(query.data.split("_")[-1])
    
    try:
        # Update user status
        update_user(user_id, {"is_active": True})
        text = get_text("user_unblocked", language_code)
    except Exception as e:
        logger.error(f"Error unblocking user {user_id}: {e}")
        text = get_text("unblock_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_user", language_code),
                callback_data=f"{USER_DETAILS}_{user_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_USER

@require_admin
async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete a user."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = int(query.data.split("_")[-1])
    
    try:
        # Delete user
        delete_user_db(user_id)
        text = get_text("user_deleted", language_code)
        
        # Return to user list
        return await user_list(update, context)
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        text = get_text("delete_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_user", language_code),
                callback_data=f"{USER_DETAILS}_{user_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_USER

@require_admin
async def reset_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Reset a user's password."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    user_id = int(query.data.split("_")[-1])
    
    try:
        # Reset password
        new_password = reset_user_password(user_id)
        text = get_text("password_reset", language_code).format(password=new_password)
    except Exception as e:
        logger.error(f"Error resetting password for user {user_id}: {e}")
        text = get_text("reset_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_user", language_code),
                callback_data=f"{USER_DETAILS}_{user_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_USER

@require_admin
async def add_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start adding a new server."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Store action in context
    context.user_data["admin_action"] = "add_server"
    
    text = get_text("enter_server_details", language_code)
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("cancel", language_code),
                callback_data=SERVERS
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return ENTERING_DETAILS

@require_admin
async def edit_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start editing a server."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    server_id = int(query.data.split("_")[-1])
    
    # Store action and server ID in context
    context.user_data["admin_action"] = "edit_server"
    context.user_data["server_id"] = server_id
    
    text = get_text("enter_server_details", language_code)
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("cancel", language_code),
                callback_data=f"{SERVER_DETAILS}_{server_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return ENTERING_DETAILS

@require_admin
async def delete_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete a server."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    server_id = int(query.data.split("_")[-1])
    
    try:
        # Delete server
        delete_server_db(server_id)
        text = get_text("server_deleted", language_code)
        
        # Return to server list
        return await server_list(update, context)
    except Exception as e:
        logger.error(f"Error deleting server {server_id}: {e}")
        text = get_text("delete_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_server", language_code),
                callback_data=f"{SERVER_DETAILS}_{server_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_SERVER

@require_admin
async def sync_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sync server with 3x-UI panel."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    server_id = int(query.data.split("_")[-1])
    
    try:
        # Get server details
        server = get_server_details(server_id)
        if not server:
            raise Exception("Server not found")
        
        # Create XUI client
        xui_client = XUIClient(
            base_url=server["panel_url"],
            username=server["panel_username"],
            password=server["panel_password"]
        )
        
        # Get server status and inbounds
        status = xui_client.get_server_status()
        inbounds = xui_client.get_inbounds()
        
        # Update server details
        update_server(server_id, {
            "is_active": True,
            "last_sync": datetime.now().isoformat(),
            "inbounds_count": len(inbounds),
            "clients_count": sum(len(inbound.get("clientStats", [])) for inbound in inbounds),
            "status": status
        })
        
        text = get_text("sync_successful", language_code)
    except Exception as e:
        logger.error(f"Error syncing server {server_id}: {e}")
        text = get_text("sync_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_server", language_code),
                callback_data=f"{SERVER_DETAILS}_{server_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_SERVER

@require_admin
async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verify a payment."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    payment_id = int(query.data.split("_")[-1])
    
    try:
        # Verify payment
        verify_payment(payment_id)
        text = get_text("payment_verified", language_code)
        
        # Return to payment list
        return await payment_list(update, context)
    except Exception as e:
        logger.error(f"Error verifying payment {payment_id}: {e}")
        text = get_text("verification_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_payment", language_code),
                callback_data=f"{PAYMENT_DETAILS}_{payment_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_PAYMENT

@require_admin
async def reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Reject a payment."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    payment_id = int(query.data.split("_")[-1])
    
    try:
        # Reject payment
        reject_payment_db(payment_id)
        text = get_text("payment_rejected", language_code)
        
        # Return to payment list
        return await payment_list(update, context)
    except Exception as e:
        logger.error(f"Error rejecting payment {payment_id}: {e}")
        text = get_text("rejection_error", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_payment", language_code),
                callback_data=f"{PAYMENT_DETAILS}_{payment_id}"
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_PAYMENT

@require_admin
async def save_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save details for server or settings."""
    language_code = context.user_data.get("language", "en")
    action = context.user_data.get("admin_action")
    
    if action == "add_server":
        try:
            # Parse server details from message
            details = parse_server_details(update.message.text)
            
            # Create server
            server = create_server(details)
            text = get_text("server_added", language_code)
            
            # Return to server list
            return await server_list(update, context)
        except Exception as e:
            logger.error(f"Error adding server: {e}")
            text = get_text("add_error", language_code)
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        get_text("try_again", language_code),
                        callback_data=SERVER_ADD
                    )
                ],
                [
                    InlineKeyboardButton(
                        get_text("back_to_servers", language_code),
                        callback_data=SERVERS
                    )
                ],
            ]
    
    elif action == "edit_server":
        try:
            # Parse server details from message
            details = parse_server_details(update.message.text)
            server_id = context.user_data.get("server_id")
            
            # Update server
            update_server(server_id, details)
            text = get_text("server_updated", language_code)
            
            # Return to server details
            return await server_details(update, context)
        except Exception as e:
            logger.error(f"Error updating server: {e}")
            text = get_text("update_error", language_code)
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        get_text("try_again", language_code),
                        callback_data=f"{SERVER_EDIT}_{server_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        get_text("back_to_server", language_code),
                        callback_data=f"{SERVER_DETAILS}_{server_id}"
                    )
                ],
            ]
    
    elif action == "edit_settings":
        try:
            # Parse settings from message
            settings = parse_system_settings(update.message.text)
            
            # Update settings
            update_system_settings(settings)
            text = get_text("settings_updated", language_code)
            
            # Return to settings menu
            return await system_settings(update, context)
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            text = get_text("update_error", language_code)
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        get_text("try_again", language_code),
                        callback_data=SETTINGS_EDIT
                    )
                ],
                [
                    InlineKeyboardButton(
                        get_text("back_to_settings", language_code),
                        callback_data=SETTINGS
                    )
                ],
            ]
    
    else:
        text = get_text("invalid_action", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_admin", language_code),
                    callback_data=ADMIN_CB
                )
            ],
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

def parse_server_details(text: str) -> Dict[str, Any]:
    """Parse server details from text input."""
    lines = text.strip().split("\n")
    details = {}
    
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        details[key] = value
    
    return details

def parse_system_settings(text: str) -> Dict[str, Any]:
    """Parse system settings from text input."""
    lines = text.strip().split("\n")
    settings = {}
    
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip().lower()
        
        if value in ["true", "yes", "on", "1"]:
            settings[key] = True
        elif value in ["false", "no", "off", "0"]:
            settings[key] = False
        else:
            try:
                settings[key] = int(value)
            except ValueError:
                settings[key] = value
    
    return settings

def get_admin_handler() -> ConversationHandler:
    """Create and return the admin conversation handler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_menu, pattern=f"^{ADMIN_CB}$")
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(user_list, pattern=f"^{USERS}$"),
                CallbackQueryHandler(server_list, pattern=f"^{SERVERS}$"),
                CallbackQueryHandler(payment_list, pattern=f"^{PAYMENTS}$"),
                CallbackQueryHandler(system_settings, pattern=f"^{SETTINGS}$"),
            ],
            SELECTING_USER: [
                CallbackQueryHandler(user_details, pattern=f"^{USER_DETAILS}_"),
                CallbackQueryHandler(block_user, pattern=f"^{USER_BLOCK}_"),
                CallbackQueryHandler(unblock_user, pattern=f"^{USER_UNBLOCK}_"),
                CallbackQueryHandler(delete_user, pattern=f"^{USER_DELETE}_"),
                CallbackQueryHandler(reset_password, pattern=f"^{USER_RESET}_"),
                CallbackQueryHandler(user_list, pattern=f"^{USERS}$"),
            ],
            SELECTING_SERVER: [
                CallbackQueryHandler(server_details, pattern=f"^{SERVER_DETAILS}_"),
                CallbackQueryHandler(add_server, pattern=f"^{SERVER_ADD}$"),
                CallbackQueryHandler(edit_server, pattern=f"^{SERVER_EDIT}_"),
                CallbackQueryHandler(delete_server, pattern=f"^{SERVER_DELETE}_"),
                CallbackQueryHandler(sync_server, pattern=f"^{SERVER_SYNC}_"),
                CallbackQueryHandler(server_list, pattern=f"^{SERVERS}$"),
            ],
            SELECTING_PAYMENT: [
                CallbackQueryHandler(payment_details, pattern=f"^{PAYMENT_DETAILS}_"),
                CallbackQueryHandler(verify_payment, pattern=f"^{PAYMENT_VERIFY}_"),
                CallbackQueryHandler(reject_payment, pattern=f"^{PAYMENT_REJECT}_"),
                CallbackQueryHandler(payment_list, pattern=f"^{PAYMENTS}$"),
            ],
            ENTERING_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_details),
                CallbackQueryHandler(admin_menu, pattern=f"^{ADMIN_CB}$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(admin_menu, pattern="^menu$"),
        ],
        name="admin",
        persistent=True
    ) 