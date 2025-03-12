"""
V2Ray account management handler for the Telegram bot.

This module implements handlers for managing V2Ray accounts including:
- Account creation
- Account renewal
- Traffic monitoring
- Account configuration
"""

import logging
import uuid
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
    update_user,
    get_user_accounts,
    create_account,
    update_account,
    get_account,
)
from utils.xui_api import XUIClient
from utils.decorators import require_auth

logger = logging.getLogger(__name__)

# XUI client configuration
XUI_CONFIG = {
    "base_url": "http://your-panel-url",  # Replace with actual panel URL
    "username": "admin",  # Replace with actual username
    "password": "password",  # Replace with actual password
}

# Initialize XUI client
xui_client = XUIClient(**XUI_CONFIG)

# Conversation states
(
    SELECTING_ACTION,
    SELECTING_PLAN,
    CONFIRMING_PURCHASE,
    PROCESSING_PAYMENT,
) = range(4)

# Callback data patterns
ACCOUNTS_CB = "accounts"
CREATE_ACCOUNT = f"{ACCOUNTS_CB}_create"
VIEW_ACCOUNTS = f"{ACCOUNTS_CB}_view"
RENEW_ACCOUNT = f"{ACCOUNTS_CB}_renew"
VIEW_DETAILS = f"{ACCOUNTS_CB}_details"
CONFIRM_PURCHASE = f"{ACCOUNTS_CB}_confirm"
CANCEL_PURCHASE = f"{ACCOUNTS_CB}_cancel"

# Account plans
PLANS = {
    "basic": {
        "name": "Basic",
        "days": 30,
        "gb": 50,
        "price": 100000,  # Price in Tomans
    },
    "premium": {
        "name": "Premium",
        "days": 30,
        "gb": 100,
        "price": 150000,
    },
    "unlimited": {
        "name": "Unlimited",
        "days": 30,
        "gb": 0,  # 0 means unlimited
        "price": 200000,
    },
}

@require_auth
async def accounts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the accounts menu."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user's accounts
    accounts = get_user_accounts(user_id)
    
    text = get_text("accounts_menu_info", language_code).format(
        account_count=len(accounts)
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("create_account", language_code),
                callback_data=CREATE_ACCOUNT
            )
        ],
        [
            InlineKeyboardButton(
                get_text("view_accounts", language_code),
                callback_data=VIEW_ACCOUNTS
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
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

@require_auth
async def create_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available account plans."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    text = get_text("select_plan", language_code)
    keyboard = []
    
    for plan_id, plan in PLANS.items():
        keyboard.append([
            InlineKeyboardButton(
                get_text("plan_button", language_code).format(
                    name=plan["name"],
                    days=plan["days"],
                    gb=plan["gb"] or "∞",
                    price=format_number(plan["price"], language_code)
                ),
                callback_data=f"{CONFIRM_PURCHASE}_{plan_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_accounts", language_code),
            callback_data=ACCOUNTS_CB
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_PLAN

@require_auth
async def confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm account purchase."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get selected plan
    plan_id = query.data.split("_")[-1]
    plan = PLANS[plan_id]
    
    # Get user's wallet balance
    user = get_user(user_id)
    balance = user.get("wallet_balance", 0)
    
    # Store plan in context
    context.user_data["selected_plan"] = plan
    
    text = get_text("confirm_purchase", language_code).format(
        plan=plan["name"],
        days=plan["days"],
        gb=plan["gb"] or "∞",
        price=format_number(plan["price"], language_code),
        balance=format_number(balance, language_code)
    )
    
    keyboard = []
    
    if balance >= plan["price"]:
        keyboard.append([
            InlineKeyboardButton(
                get_text("confirm_purchase_button", language_code),
                callback_data=f"{CONFIRM_PURCHASE}_confirm"
            )
        ])
    else:
        # Not enough balance, show add funds button
        keyboard.append([
            InlineKeyboardButton(
                get_text("add_funds", language_code),
                callback_data="payments"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            get_text("cancel_purchase", language_code),
            callback_data=CANCEL_PURCHASE
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return CONFIRMING_PURCHASE

@require_auth
async def process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process account purchase."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get selected plan
    plan = context.user_data.get("selected_plan")
    if not plan:
        text = get_text("invalid_plan", language_code)
        await query.edit_message_text(text=text)
        return ConversationHandler.END
    
    # Get user's wallet balance
    user = get_user(user_id)
    balance = user.get("wallet_balance", 0)
    
    if balance < plan["price"]:
        text = get_text("insufficient_balance", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("add_funds", language_code),
                    callback_data="payments"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_accounts", language_code),
                    callback_data=ACCOUNTS_CB
                )
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        return SELECTING_ACTION
    
    try:
        # Create V2Ray account
        email = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
        client = xui_client.create_client(
            inbound_id=1,  # Replace with actual inbound ID
            email=email,
            telegram_id=str(user_id),
            total_gb=plan["gb"],
            expire_days=plan["days"]
        )
        
        if not client:
            raise Exception("Failed to create V2Ray account")
        
        # Create account record in database
        account = create_account(
            user_id=user_id,
            email=email,
            inbound_id=1,  # Replace with actual inbound ID
            plan_id=plan["name"],
            traffic_limit=plan["gb"],
            expiry_days=plan["days"],
            price=plan["price"]
        )
        
        # Update user's wallet balance
        new_balance = balance - plan["price"]
        update_user(user_id, {"wallet_balance": new_balance})
        
        text = get_text("purchase_successful", language_code).format(
            plan=plan["name"],
            config=client.get("config", ""),  # Replace with actual config generation
            balance=format_number(new_balance, language_code)
        )
        
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        text = get_text("purchase_failed", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_accounts", language_code),
                callback_data=ACCOUNTS_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

@require_auth
async def view_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's accounts."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user's accounts
    accounts = get_user_accounts(user_id)
    
    if not accounts:
        text = get_text("no_accounts", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("create_account", language_code),
                    callback_data=CREATE_ACCOUNT
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_accounts", language_code),
                    callback_data=ACCOUNTS_CB
                )
            ],
        ]
    else:
        text = get_text("accounts_list", language_code)
        keyboard = []
        
        for account in accounts:
            # Get traffic usage
            traffic = xui_client.get_client_traffic(account["email"])
            used_gb = traffic.get("up", 0) + traffic.get("down", 0) / (1024 * 1024 * 1024)
            total_gb = account["traffic_limit"] or "∞"
            
            keyboard.append([
                InlineKeyboardButton(
                    get_text("account_button", language_code).format(
                        plan=account["plan_id"],
                        used=format_number(used_gb, language_code),
                        total=total_gb
                    ),
                    callback_data=f"{VIEW_DETAILS}_{account['id']}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(
                get_text("create_account", language_code),
                callback_data=CREATE_ACCOUNT
            )
        ])
        
        keyboard.append([
            InlineKeyboardButton(
                get_text("back_to_accounts", language_code),
                callback_data=ACCOUNTS_CB
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

@require_auth
async def view_account_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show account details."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get account ID from callback data
    account_id = int(query.data.split("_")[-1])
    account = get_account(account_id)
    
    if not account or account["user_id"] != user_id:
        text = get_text("invalid_account", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_accounts", language_code),
                    callback_data=ACCOUNTS_CB
                )
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        return SELECTING_ACTION
    
    # Get traffic usage
    traffic = xui_client.get_client_traffic(account["email"])
    used_gb = traffic.get("up", 0) + traffic.get("down", 0) / (1024 * 1024 * 1024)
    total_gb = account["traffic_limit"] or "∞"
    
    text = get_text("account_details", language_code).format(
        plan=account["plan_id"],
        created=format_date(account["created_at"], language_code),
        expires=format_date(account["expiry_date"], language_code),
        used=format_number(used_gb, language_code),
        total=total_gb,
        config=account["config"]
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("renew_account", language_code),
                callback_data=f"{RENEW_ACCOUNT}_{account_id}"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_accounts", language_code),
                callback_data=VIEW_ACCOUNTS
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

@require_auth
async def renew_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start account renewal process."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get account ID from callback data
    account_id = int(query.data.split("_")[-1])
    account = get_account(account_id)
    
    if not account or account["user_id"] != user_id:
        text = get_text("invalid_account", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_accounts", language_code),
                    callback_data=ACCOUNTS_CB
                )
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        return SELECTING_ACTION
    
    # Store account in context
    context.user_data["renew_account"] = account
    
    # Show renewal plans
    text = get_text("select_renewal_plan", language_code)
    keyboard = []
    
    for plan_id, plan in PLANS.items():
        if plan["name"] == account["plan_id"]:
            keyboard.append([
                InlineKeyboardButton(
                    get_text("renewal_plan_button", language_code).format(
                        days=plan["days"],
                        price=format_number(plan["price"], language_code)
                    ),
                    callback_data=f"{CONFIRM_PURCHASE}_renew_{plan_id}"
                )
            ])
    
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_account", language_code),
            callback_data=f"{VIEW_DETAILS}_{account_id}"
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_PLAN

def get_accounts_handler() -> ConversationHandler:
    """Create and return the accounts conversation handler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(accounts_menu, pattern=f"^{ACCOUNTS_CB}$")
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(create_account, pattern=f"^{CREATE_ACCOUNT}$"),
                CallbackQueryHandler(view_accounts, pattern=f"^{VIEW_ACCOUNTS}$"),
                CallbackQueryHandler(view_account_details, pattern=f"^{VIEW_DETAILS}_"),
                CallbackQueryHandler(renew_account, pattern=f"^{RENEW_ACCOUNT}_"),
            ],
            SELECTING_PLAN: [
                CallbackQueryHandler(confirm_purchase, pattern=f"^{CONFIRM_PURCHASE}_"),
                CallbackQueryHandler(accounts_menu, pattern=f"^{ACCOUNTS_CB}$"),
            ],
            CONFIRMING_PURCHASE: [
                CallbackQueryHandler(process_purchase, pattern=f"^{CONFIRM_PURCHASE}_confirm$"),
                CallbackQueryHandler(create_account, pattern=f"^{CANCEL_PURCHASE}$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(accounts_menu, pattern="^menu$"),
        ],
        name="accounts",
        persistent=True
    ) 