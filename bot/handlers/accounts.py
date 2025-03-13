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
import os
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
    "base_url": os.getenv("XUI_PANEL_URL", "http://localhost:8080"),
    "username": os.getenv("XUI_PANEL_USERNAME", "admin"),
    "password": os.getenv("XUI_PANEL_PASSWORD", "admin"),
}

# Initialize XUI client
try:
    xui_client = XUIClient(**XUI_CONFIG)
except Exception as e:
    logger.error(f"Failed to initialize XUI client: {e}")
    xui_client = None

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
    """Handle account creation - show available plans."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Check if user has wallet balance for any plan
    user = get_user(user_id)
    wallet_balance = user.get("wallet_balance", 0)
    
    # Create message with available plans
    message = get_text("available_plans", language_code) + "\n\n"
    
    # Add plans to message and keyboard
    keyboard = []
    
    for plan_id, plan in PLANS.items():
        plan_name = plan["name"]
        plan_days = plan["days"]
        plan_gb = plan["gb"]
        plan_price = plan["price"]
        
        # Format plan details
        if plan_gb == 0:
            plan_gb_text = get_text("unlimited_traffic", language_code)
        else:
            plan_gb_text = f"{plan_gb} GB"
        
        message += f"*{plan_name}*\n"
        message += f"📆 {plan_days} " + get_text("days", language_code) + "\n"
        message += f"📊 {plan_gb_text}\n"
        message += f"💰 {format_number(plan_price, language_code)} " + get_text("currency", language_code) + "\n\n"
        
        # Check if user can afford this plan
        can_afford = wallet_balance >= plan_price
        button_text = f"{plan_name} ({format_number(plan_price, language_code)} " + get_text("currency", language_code) + ")"
        
        # Add to keyboard if affordable or not
        if can_afford:
            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"{ACCOUNTS_CB}_plan:{plan_id}"
                )
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(
                    button_text + " ❌",
                    callback_data=f"{ACCOUNTS_CB}_insufficient:{plan_id}"
                )
            ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_accounts", language_code),
            callback_data=ACCOUNTS_CB
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_PLAN

@require_auth
async def confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm account purchase."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get selected plan from callback data
    callback_data = query.data
    plan_id = callback_data.split(":")[-1]
    
    # Check if this is the insufficient funds callback
    if "insufficient" in callback_data:
        # Show payment options
        plan = PLANS.get(plan_id)
        plan_price = plan["price"]
        user = get_user(user_id)
        wallet_balance = user.get("wallet_balance", 0)
        
        missing_amount = plan_price - wallet_balance
        
        # Message about insufficient funds
        message = get_text("insufficient_funds", language_code).format(
            balance=format_number(wallet_balance, language_code),
            price=format_number(plan_price, language_code),
            missing=format_number(missing_amount, language_code)
        )
        
        # Keyboard for adding funds
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("add_funds", language_code),
                    callback_data=PAYMENTS_CB
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_plans", language_code),
                    callback_data=CREATE_ACCOUNT
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SELECTING_PLAN
    
    # Get plan details
    plan = PLANS.get(plan_id)
    if not plan:
        # Invalid plan
        await query.edit_message_text(
            text=get_text("invalid_plan", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_PLAN
    
    # Store selected plan in context
    context.user_data["selected_plan"] = plan_id
    
    # Confirm purchase
    message = get_text("confirm_purchase", language_code).format(
        plan_name=plan["name"],
        days=plan["days"],
        gb=plan["gb"] if plan["gb"] > 0 else get_text("unlimited", language_code),
        price=format_number(plan["price"], language_code)
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("confirm", language_code),
                callback_data=CONFIRM_PURCHASE
            ),
            InlineKeyboardButton(
                get_text("cancel", language_code),
                callback_data=CANCEL_PURCHASE
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CONFIRMING_PURCHASE

@require_auth
async def process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process account purchase."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get selected plan
    plan_id = context.user_data.get("selected_plan")
    if not plan_id or plan_id not in PLANS:
        await query.edit_message_text(
            text=get_text("invalid_plan", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_PLAN
    
    plan = PLANS[plan_id]
    
    # Verify user has sufficient balance
    user = get_user(user_id)
    wallet_balance = user.get("wallet_balance", 0)
    
    if wallet_balance < plan["price"]:
        # Insufficient funds
        message = get_text("insufficient_funds", language_code).format(
            balance=format_number(wallet_balance, language_code),
            price=format_number(plan["price"], language_code),
            missing=format_number(plan["price"] - wallet_balance, language_code)
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("add_funds", language_code),
                    callback_data=PAYMENTS_CB
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_accounts", language_code),
                    callback_data=ACCOUNTS_CB
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SELECTING_PLAN
    
    # Create transaction for account purchase
    transaction_id = create_transaction(
        user_id=user_id,
        amount=plan["price"],
        payment_method="wallet",
        description=f"Purchase of {plan['name']} plan",
        transaction_type="purchase"
    )
    
    if not transaction_id:
        # Transaction creation failed
        await query.edit_message_text(
            text=get_text("transaction_error", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_PLAN
    
    # Generate a random name for the account
    account_name = f"Account-{uuid.uuid4().hex[:8]}"
    
    # Create account
    account_id = create_account(
        user_id=user_id,
        plan_id=plan_id,
        server_id=1,  # Default server
        name=account_name,
        transaction_id=transaction_id
    )
    
    if not account_id:
        # Account creation failed
        update_transaction(transaction_id, status="failed")
        
        await query.edit_message_text(
            text=get_text("account_creation_error", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_PLAN
    
    # Get the created account
    account = get_account(account_id)
    
    if not account:
        # Account not found
        await query.edit_message_text(
            text=get_text("account_retrieval_error", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_PLAN
    
    # Show account details to user
    expiry_date = account.get("expiry_date", "")
    traffic_limit = account.get("traffic_limit", 0)
    config_url = account.get("config_url", "")
    
    if traffic_limit == 0:
        traffic_text = get_text("unlimited", language_code)
    else:
        traffic_text = f"{traffic_limit} GB"
    
    message = get_text("account_created", language_code).format(
        plan_name=plan["name"],
        expiry_date=format_date(expiry_date, language_code),
        traffic=traffic_text
    )
    
    # Create QR code if a configuration URL is available
    if config_url:
        message += "\n\n" + get_text("account_config_info", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("view_accounts", language_code),
                callback_data=VIEW_ACCOUNTS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_accounts", language_code),
                callback_data=ACCOUNTS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # If there's a configuration URL, send it as a separate message with QR code
    if config_url:
        import segno
        
        # Create QR code
        qr = segno.make(config_url)
        qr_file = f"/tmp/qr_{account_id}.png"
        qr.save(qr_file, scale=5)
        
        # Send config url and QR code
        with open(qr_file, "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=get_text("account_config_url", language_code).format(url=config_url),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Clean up
        try:
            os.remove(qr_file)
        except Exception as e:
            logger.error(f"Error removing QR code file: {e}")
    
    return SELECTING_ACTION

@require_auth
async def view_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the user's accounts."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user's accounts
    accounts = get_user_accounts(user_id)
    
    if not accounts:
        # No accounts
        message = get_text("no_accounts", language_code)
        
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
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SELECTING_ACTION
    
    # Format accounts
    message = get_text("your_accounts", language_code) + "\n\n"
    
    keyboard = []
    
    for account in accounts:
        account_id = account.get("id")
        account_name = account.get("name", "Unknown")
        status = account.get("status", "active")
        status_text = get_text(f"status_{status}", language_code)
        
        # Format account expiry and traffic
        expiry_date = account.get("expiry_date", "")
        traffic_used = account.get("traffic_used", 0)
        traffic_limit = account.get("traffic_limit", 0)
        
        if traffic_limit == 0:
            traffic_text = f"{format_number(traffic_used / 1024 / 1024 / 1024, language_code)} GB / " + get_text("unlimited", language_code)
        else:
            traffic_used_gb = traffic_used / 1024 / 1024 / 1024
            traffic_limit_gb = traffic_limit
            traffic_text = f"{format_number(traffic_used_gb, language_code)} / {format_number(traffic_limit_gb, language_code)} GB"
        
        # Add account to message
        message += f"*{account_name}*\n"
        message += f"📊 {status_text}\n"
        message += f"📅 {format_date(expiry_date, language_code)}\n"
        message += f"💾 {traffic_text}\n\n"
        
        # Add button for this account
        keyboard.append([
            InlineKeyboardButton(
                account_name,
                callback_data=f"{VIEW_DETAILS}:{account_id}"
            )
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_accounts", language_code),
            callback_data=ACCOUNTS_CB
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_ACTION

@require_auth
async def view_account_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show details for a specific account."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get account ID from callback data
    account_id = query.data.split(":")[-1]
    
    # Get account details
    account = get_account(account_id)
    
    if not account:
        # Account not found
        await query.edit_message_text(
            text=get_text("account_not_found", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_ACTION
    
    # Check if this account belongs to the user
    if account.get("user_id") != user_id:
        await query.edit_message_text(
            text=get_text("account_not_authorized", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_ACTION
    
    # Format account details
    account_name = account.get("name", "Unknown")
    status = account.get("status", "active")
    status_text = get_text(f"status_{status}", language_code)
    
    expiry_date = account.get("expiry_date", "")
    traffic_used = account.get("traffic_used", 0)
    traffic_limit = account.get("traffic_limit", 0)
    
    traffic_used_gb = traffic_used / 1024 / 1024 / 1024
    
    # Get config URL
    config_url = account.get("config_url", "")
    
    # Create message
    message = get_text("account_details", language_code).format(
        name=account_name,
        status=status_text,
        expiry_date=format_date(expiry_date, language_code),
        traffic_used=format_number(traffic_used_gb, language_code)
    )
    
    # Add traffic limit info
    if traffic_limit == 0:
        message += get_text("traffic_unlimited", language_code)
    else:
        traffic_limit_gb = traffic_limit
        traffic_percent = min(100, int((traffic_used_gb / traffic_limit_gb) * 100))
        message += get_text("traffic_limited", language_code).format(
            used=format_number(traffic_used_gb, language_code),
            limit=format_number(traffic_limit_gb, language_code),
            percent=traffic_percent
        )
    
    # Add config info
    if config_url:
        message += "\n\n" + get_text("account_config_available", language_code)
    else:
        message += "\n\n" + get_text("account_config_unavailable", language_code)
    
    # Create keyboard
    keyboard = []
    
    # Add renew button if account is active or expired
    if status in ["active", "expired"]:
        keyboard.append([
            InlineKeyboardButton(
                get_text("renew_account", language_code),
                callback_data=f"{RENEW_ACCOUNT}:{account_id}"
            )
        ])
    
    # Add config button if config URL is available
    if config_url:
        keyboard.append([
            InlineKeyboardButton(
                get_text("show_config", language_code),
                callback_data=f"{ACCOUNTS_CB}_config:{account_id}"
            )
        ])
    
    # Add back buttons
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_accounts_list", language_code),
            callback_data=VIEW_ACCOUNTS
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            get_text("back_to_accounts", language_code),
            callback_data=ACCOUNTS_CB
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_ACTION

@require_auth
async def renew_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle account renewal process."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get account ID from callback data
    account_id = query.data.split(":")[-1]
    
    # Get account details
    account = get_account(account_id)
    
    if not account:
        # Account not found
        await query.edit_message_text(
            text=get_text("account_not_found", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_ACTION
    
    # Check if this account belongs to the user
    if account.get("user_id") != user_id:
        await query.edit_message_text(
            text=get_text("account_not_authorized", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_ACTION
    
    # Get the plan for this account
    plan_id = account.get("plan_id")
    plan = get_plan(plan_id)
    
    if not plan:
        await query.edit_message_text(
            text=get_text("plan_not_found", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_ACTION
    
    # Get user's wallet balance
    wallet_balance = get_user_wallet_balance(user_id)
    plan_price = plan.get("price", 0)
    
    # Store in context for later use
    context.user_data["renew"] = {
        "account_id": account_id,
        "plan_id": plan_id,
        "price": plan_price
    }
    
    # Format plan details
    plan_name = plan.get("name", "Unknown")
    plan_duration = plan.get("duration", 30)
    plan_traffic = plan.get("traffic", 0)
    
    if plan_traffic == 0:
        traffic_text = get_text("unlimited", language_code)
    else:
        traffic_text = f"{format_number(plan_traffic, language_code)} GB"
    
    # Create message
    message = get_text("renew_account_confirm", language_code).format(
        name=account.get("name", "Unknown"),
        plan=plan_name,
        duration=plan_duration,
        traffic=traffic_text,
        price=format_number(plan_price, language_code)
    )
    
    # Check if user has enough balance
    if wallet_balance < plan_price:
        missing_amount = plan_price - wallet_balance
        message += "\n\n" + get_text("insufficient_balance", language_code).format(
            balance=format_number(wallet_balance, language_code),
            missing=format_number(missing_amount, language_code)
        )
        
        # Create keyboard with add funds option
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("add_funds", language_code),
                    callback_data=PAYMENTS_CB
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_account", language_code),
                    callback_data=f"{VIEW_DETAILS}:{account_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_accounts", language_code),
                    callback_data=ACCOUNTS_CB
                )
            ]
        ]
    else:
        # Create keyboard with confirm option
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("confirm_renew", language_code),
                    callback_data=f"{CONFIRM_RENEW}:{account_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_account", language_code),
                    callback_data=f"{VIEW_DETAILS}:{account_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_accounts", language_code),
                    callback_data=ACCOUNTS_CB
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
async def confirm_renew(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm and process account renewal."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get account ID from callback data
    account_id = query.data.split(":")[-1]
    
    # Get renew data from context
    renew_data = context.user_data.get("renew", {})
    
    if not renew_data or renew_data.get("account_id") != account_id:
        await query.edit_message_text(
            text=get_text("renew_error", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_ACTION
    
    # Get account details
    account = get_account(account_id)
    
    if not account:
        # Account not found
        await query.edit_message_text(
            text=get_text("account_not_found", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_ACTION
    
    # Check if this account belongs to the user
    if account.get("user_id") != user_id:
        await query.edit_message_text(
            text=get_text("account_not_authorized", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return SELECTING_ACTION
    
    # Get plan details
    plan_id = renew_data.get("plan_id")
    plan_price = renew_data.get("price", 0)
    
    # Check user's wallet balance
    wallet_balance = get_user_wallet_balance(user_id)
    
    if wallet_balance < plan_price:
        missing_amount = plan_price - wallet_balance
        message = get_text("insufficient_balance", language_code).format(
            balance=format_number(wallet_balance, language_code),
            missing=format_number(missing_amount, language_code)
        )
        
        # Create keyboard with add funds option
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("add_funds", language_code),
                    callback_data=PAYMENTS_CB
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_account", language_code),
                    callback_data=f"{VIEW_DETAILS}:{account_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_accounts", language_code),
                    callback_data=ACCOUNTS_CB
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
    
    try:
        # Create transaction
        transaction = create_transaction(
            user_id=user_id,
            amount=-plan_price,
            description=get_text("transaction_renew_account", language_code).format(
                name=account.get("name", "Unknown")
            ),
            transaction_type="renew_account"
        )
        
        # Renew account
        renewed_account = renew_account_api(account_id)
        
        if not renewed_account:
            # Refund the transaction if renewal failed
            refund_transaction = create_transaction(
                user_id=user_id,
                amount=plan_price,
                description=get_text("transaction_renew_refund", language_code).format(
                    name=account.get("name", "Unknown")
                ),
                transaction_type="refund"
            )
            
            message = get_text("renew_failed", language_code).format(
                name=account.get("name", "Unknown")
            )
        else:
            # Get updated account info
            updated_account = get_account(account_id)
            
            message = get_text("renew_success", language_code).format(
                name=updated_account.get("name", "Unknown"),
                expiry_date=format_date(updated_account.get("expiry_date", ""), language_code)
            )
    except Exception as e:
        logger.error(f"Error renewing account: {e}")
        message = get_text("renew_error", language_code)
    
    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("view_account", language_code),
                callback_data=f"{VIEW_DETAILS}:{account_id}"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_accounts", language_code),
                callback_data=ACCOUNTS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Clear renewal data from context
    if "renew" in context.user_data:
        del context.user_data["renew"]
    
    return SELECTING_ACTION

def get_accounts_handler() -> ConversationHandler:
    """Create and return the accounts conversation handler."""
    accounts_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                accounts_menu, pattern=f"^{ACCOUNTS_CB}$"
            )
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(view_accounts, pattern=f"^{VIEW_ACCOUNTS}$"),
                CallbackQueryHandler(create_account, pattern=f"^{CREATE_ACCOUNT}$"),
                CallbackQueryHandler(view_account_details, pattern=f"^{VIEW_DETAILS}:"),
                CallbackQueryHandler(show_account_config, pattern=f"^{ACCOUNTS_CB}_config:"),
                CallbackQueryHandler(confirm_purchase, pattern=f"^{CONFIRM_PURCHASE}:"),
                CallbackQueryHandler(process_purchase, pattern=f"^{CONFIRM_PURCHASE}:"),
                CallbackQueryHandler(renew_account, pattern=f"^{RENEW_ACCOUNT}:"),
                CallbackQueryHandler(confirm_renew, pattern=f"^{CONFIRM_RENEW}:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_amount)
            ],
            ACCOUNT_CREATED: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_account_name)
            ]
        },
        fallbacks=[
            CallbackQueryHandler(back_to_main, pattern=f"^{BACK_CB}$"),
            CommandHandler("start", start)
        ],
        map_to_parent={
            END: SELECTING_FEATURE,
        },
        name="accounts_conversation",
        persistent=True
    )
    
    return accounts_handler 