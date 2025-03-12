"""
Payment processing handler for the V2Ray Telegram bot.

This module implements handlers for payment operations including:
- Card-to-card payments
- Zarinpal payments
- Payment verification
- Transaction history
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
    update_user,
    create_transaction,
    get_user_transactions,
    get_transaction,
    update_transaction,
)
from utils.zarinpal import create_payment, verify_payment
from utils.decorators import require_auth

logger = logging.getLogger(__name__)

# Conversation states
(
    SELECTING_ACTION,
    SELECTING_METHOD,
    ENTERING_AMOUNT,
    CONFIRMING_PAYMENT,
    ENTERING_RECEIPT,
    VERIFYING_PAYMENT,
) = range(6)

# Callback data patterns
PAYMENTS_CB = "payments"
CARD_PAYMENT = f"{PAYMENTS_CB}_card"
ZARINPAL_PAYMENT = f"{PAYMENTS_CB}_zarinpal"
TRANSACTION_HISTORY = f"{PAYMENTS_CB}_history"
VERIFY_PAYMENT = f"{PAYMENTS_CB}_verify"
CANCEL_PAYMENT = f"{PAYMENTS_CB}_cancel"

# Card payment details
CARD_NUMBER = "6037997599999999"  # Replace with actual card number
CARD_HOLDER = "نام صاحب حساب"  # Replace with actual card holder name
BANK_NAME = "بانک"  # Replace with actual bank name

@require_auth
async def payments_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the payments menu."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user's wallet balance
    user = get_user(user_id)
    balance = user.get("wallet_balance", 0)
    
    text = get_text("payments_menu_info", language_code).format(
        balance=format_number(balance, language_code)
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("card_payment", language_code),
                callback_data=CARD_PAYMENT
            )
        ],
        [
            InlineKeyboardButton(
                get_text("zarinpal_payment", language_code),
                callback_data=ZARINPAL_PAYMENT
            )
        ],
        [
            InlineKeyboardButton(
                get_text("transaction_history", language_code),
                callback_data=TRANSACTION_HISTORY
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
    
    return SELECTING_METHOD

@require_auth
async def card_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show card payment information."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    text = get_text("card_payment_info", language_code).format(
        card_number=CARD_NUMBER,
        card_holder=CARD_HOLDER,
        bank_name=BANK_NAME
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("submit_receipt", language_code),
                callback_data=VERIFY_PAYMENT
            )
        ],
        [
            InlineKeyboardButton(
                get_text("cancel_payment", language_code),
                callback_data=CANCEL_PAYMENT
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return ENTERING_RECEIPT

@require_auth
async def zarinpal_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start Zarinpal payment process."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    text = get_text("enter_payment_amount", language_code)
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("cancel_payment", language_code),
                callback_data=CANCEL_PAYMENT
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return ENTERING_AMOUNT

@require_auth
async def process_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the entered payment amount."""
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    amount_text = update.message.text
    
    try:
        amount = int(amount_text)
        if amount < 10000:  # Minimum amount in Tomans
            text = get_text("amount_too_small", language_code)
            return ENTERING_AMOUNT
        
        # Create Zarinpal payment
        payment_url = create_payment(amount, user_id)
        if not payment_url:
            text = get_text("payment_creation_failed", language_code)
            return SELECTING_METHOD
        
        text = get_text("payment_link_info", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("pay_now", language_code),
                    url=payment_url
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("verify_payment", language_code),
                    callback_data=VERIFY_PAYMENT
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("cancel_payment", language_code),
                    callback_data=CANCEL_PAYMENT
                )
            ],
        ]
        
    except ValueError:
        text = get_text("invalid_amount", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("try_again", language_code),
                    callback_data=ZARINPAL_PAYMENT
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("cancel_payment", language_code),
                    callback_data=CANCEL_PAYMENT
                )
            ],
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    
    return VERIFYING_PAYMENT

@require_auth
async def process_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the submitted payment receipt."""
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Check if a photo was sent
    if not update.message.photo:
        text = get_text("receipt_photo_required", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("try_again", language_code),
                    callback_data=CARD_PAYMENT
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("cancel_payment", language_code),
                    callback_data=CANCEL_PAYMENT
                )
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text=text, reply_markup=reply_markup)
        return ENTERING_RECEIPT
    
    # Get the largest photo (best quality)
    photo = update.message.photo[-1]
    
    # Create a pending transaction
    transaction = create_transaction(
        user_id=user_id,
        amount=0,  # Will be updated by admin
        payment_method="card",
        status="pending",
        receipt_id=photo.file_id
    )
    
    # Notify admin about new receipt (implement in admin handler)
    
    text = get_text("receipt_submitted", language_code)
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_METHOD

@require_auth
async def verify_zarinpal_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verify a Zarinpal payment."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get the latest pending Zarinpal transaction
    transaction = get_transaction(user_id, "zarinpal", "pending")
    if not transaction:
        text = get_text("no_pending_payment", language_code)
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_payments", language_code),
                    callback_data=PAYMENTS_CB
                )
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        return SELECTING_METHOD
    
    # Verify payment with Zarinpal
    if verify_payment(transaction["payment_id"]):
        # Update transaction status
        update_transaction(transaction["id"], {"status": "completed"})
        
        # Update user's wallet balance
        user = get_user(user_id)
        new_balance = user.get("wallet_balance", 0) + transaction["amount"]
        update_user(user_id, {"wallet_balance": new_balance})
        
        text = get_text("payment_successful", language_code).format(
            amount=format_number(transaction["amount"], language_code),
            balance=format_number(new_balance, language_code)
        )
    else:
        text = get_text("payment_verification_failed", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_METHOD

@require_auth
async def transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's transaction history."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user's transactions
    transactions = get_user_transactions(user_id)
    
    if not transactions:
        text = get_text("no_transactions", language_code)
    else:
        text = get_text("transaction_history_header", language_code) + "\n\n"
        for tx in transactions:
            text += get_text("transaction_item", language_code).format(
                date=format_date(tx["created_at"], language_code),
                amount=format_number(tx["amount"], language_code),
                method=get_text(f"payment_method_{tx['payment_method']}", language_code),
                status=get_text(f"payment_status_{tx['status']}", language_code)
            ) + "\n"
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_METHOD

@require_auth
async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current payment process."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    text = get_text("payment_cancelled", language_code)
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_METHOD

def get_payments_handler() -> ConversationHandler:
    """Create and return the payments conversation handler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(payments_menu, pattern=f"^{PAYMENTS_CB}$")
        ],
        states={
            SELECTING_METHOD: [
                CallbackQueryHandler(card_payment, pattern=f"^{CARD_PAYMENT}$"),
                CallbackQueryHandler(zarinpal_payment, pattern=f"^{ZARINPAL_PAYMENT}$"),
                CallbackQueryHandler(transaction_history, pattern=f"^{TRANSACTION_HISTORY}$"),
            ],
            ENTERING_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_amount),
                CallbackQueryHandler(cancel_payment, pattern=f"^{CANCEL_PAYMENT}$"),
            ],
            ENTERING_RECEIPT: [
                MessageHandler(filters.PHOTO, process_receipt),
                CallbackQueryHandler(cancel_payment, pattern=f"^{CANCEL_PAYMENT}$"),
            ],
            VERIFYING_PAYMENT: [
                CallbackQueryHandler(verify_zarinpal_payment, pattern=f"^{VERIFY_PAYMENT}$"),
                CallbackQueryHandler(cancel_payment, pattern=f"^{CANCEL_PAYMENT}$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(payments_menu, pattern="^menu$"),
            CallbackQueryHandler(cancel_payment, pattern=f"^{CANCEL_PAYMENT}$"),
        ],
        name="payments",
        persistent=True
    ) 