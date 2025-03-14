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
    get_all_users,
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
    """Handle card payment selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Setup payment information in context
    context.user_data["payment_method"] = "card"
    
    # Display card payment information
    message = get_text("card_payment_info", language_code).format(
        card_number=CARD_NUMBER,
        card_holder=CARD_HOLDER,
        bank_name=BANK_NAME
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("enter_amount", language_code),
                callback_data=f"{PAYMENTS_CB}_enter_amount"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return ENTERING_AMOUNT

@require_auth
async def zarinpal_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Zarinpal payment selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Setup payment information in context
    context.user_data["payment_method"] = "zarinpal"
    
    # Display Zarinpal payment information
    message = get_text("zarinpal_payment_info", language_code)
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("enter_amount", language_code),
                callback_data=f"{PAYMENTS_CB}_enter_amount"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return ENTERING_AMOUNT

@require_auth
async def process_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the entered payment amount."""
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Check if coming from callback query or message
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        # Ask for amount
        message = get_text("enter_payment_amount", language_code)
        
        await query.edit_message_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ENTERING_AMOUNT
    
    # If message, process the amount
    try:
        amount = int(update.message.text.strip())
        
        # Validate amount (minimum 10,000 Tomans)
        if amount < 10000:
            await update.message.reply_text(
                get_text("min_payment_amount_error", language_code).format(min_amount=10000),
                parse_mode=ParseMode.MARKDOWN
            )
            return ENTERING_AMOUNT
        
        # Store amount in context
        context.user_data["payment_amount"] = amount
        payment_method = context.user_data.get("payment_method")
        
        # Confirm payment
        message = get_text("confirm_payment", language_code).format(
            amount=format_number(amount, language_code),
            method=get_text(f"{payment_method}_payment_name", language_code)
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("confirm", language_code),
                    callback_data=f"{PAYMENTS_CB}_confirm"
                ),
                InlineKeyboardButton(
                    get_text("cancel", language_code),
                    callback_data=CANCEL_PAYMENT
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return CONFIRMING_PAYMENT
        
    except ValueError:
        # Invalid amount
        await update.message.reply_text(
            get_text("invalid_amount", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return ENTERING_AMOUNT

@require_auth
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process payment confirmation."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    payment_method = context.user_data.get("payment_method")
    amount = context.user_data.get("payment_amount")
    
    # Process payment based on method
    if payment_method == "card":
        # Create card payment transaction
        transaction_id = create_transaction(
            user_id=user_id,
            amount=amount,
            payment_method="card",
            description="Card payment from Telegram bot"
        )
        
        if not transaction_id:
            await query.edit_message_text(
                get_text("payment_creation_error", language_code),
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        # Store transaction ID in context
        context.user_data["transaction_id"] = transaction_id
        
        # Ask user to upload receipt
        message = get_text("card_payment_instructions", language_code).format(
            amount=format_number(amount, language_code),
            card_number=CARD_NUMBER,
            card_holder=CARD_HOLDER,
            bank_name=BANK_NAME
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("cancel_payment", language_code),
                    callback_data=CANCEL_PAYMENT
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ENTERING_RECEIPT
        
    elif payment_method == "zarinpal":
        # Create Zarinpal payment
        result = create_payment(
            user_id=user_id,
            amount=amount,
            description="Zarinpal payment from Telegram bot"
        )
        
        if not result or not result.get("success"):
            error_message = result.get("error_message", "Unknown error") if result else "Payment creation failed"
            await query.edit_message_text(
                get_text("payment_creation_error", language_code) + f"\n\n{error_message}",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        # Get payment link and transaction ID
        payment_url = result.get("payment_url")
        transaction_id = result.get("transaction_id")
        
        # Store transaction ID in context
        context.user_data["transaction_id"] = transaction_id
        
        # Send payment link
        message = get_text("zarinpal_payment_link", language_code)
        
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
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return VERIFYING_PAYMENT
    
    else:
        # Unsupported payment method
        await query.edit_message_text(
            get_text("unsupported_payment_method", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

@require_auth
async def process_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the receipt information for card payments."""
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    transaction_id = context.user_data.get("transaction_id")
    
    if not update.message:
        # Expecting a text message with receipt information
        await update.callback_query.edit_message_text(
            get_text("enter_receipt_info", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return ENTERING_RECEIPT
    
    # Get receipt information (tracking number)
    tracking_number = update.message.text.strip()
    
    # Validate tracking number
    if not tracking_number or len(tracking_number) < 4:
        await update.message.reply_text(
            get_text("invalid_receipt", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return ENTERING_RECEIPT
    
    # Update transaction with receipt information
    success = update_transaction(
        transaction_id,
        receipt_number=tracking_number,
        status="pending_verification"
    )
    
    if not success:
        await update.message.reply_text(
            get_text("receipt_update_error", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return ENTERING_RECEIPT
    
    # Send confirmation to user
    message = get_text("receipt_submitted", language_code).format(
        transaction_id=transaction_id,
        tracking_number=tracking_number
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("check_payment_status", language_code),
                callback_data=f"{PAYMENTS_CB}_check:{transaction_id}"
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Notify admins about the new payment
    await notify_admins_new_payment(context.bot, transaction_id, "card", user_id)
    
    return ConversationHandler.END

@require_auth
async def verify_zarinpal_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verify a Zarinpal payment."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    transaction_id = context.user_data.get("transaction_id")
    
    if not transaction_id:
        await query.edit_message_text(
            get_text("no_transaction_id", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    # Check transaction status
    transaction = get_transaction(transaction_id)
    
    if not transaction:
        await query.edit_message_text(
            get_text("transaction_not_found", language_code),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    status = transaction.get("status")
    
    if status == "completed":
        # Payment successful
        message = get_text("payment_successful", language_code).format(
            amount=format_number(transaction.get("amount"), language_code),
            transaction_id=transaction_id,
            date=format_date(transaction.get("updated_at"), language_code)
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back_to_payments", language_code),
                    callback_data=PAYMENTS_CB
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ConversationHandler.END
        
    elif status == "failed":
        # Payment failed
        message = get_text("payment_failed", language_code).format(
            transaction_id=transaction_id
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("try_again", language_code),
                    callback_data=PAYMENTS_CB
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ConversationHandler.END
        
    else:
        # Payment still processing
        message = get_text("payment_processing", language_code).format(
            transaction_id=transaction_id
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("check_again", language_code),
                    callback_data=VERIFY_PAYMENT
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back_to_payments", language_code),
                    callback_data=PAYMENTS_CB
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return VERIFYING_PAYMENT

@require_auth
async def transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the user's transaction history."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = context.user_data.get("language", "en")
    
    # Get user's transactions
    transactions = get_user_transactions(user_id, limit=10)
    
    if not transactions:
        # No transactions
        message = get_text("no_transactions", language_code)
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("add_funds", language_code),
                    callback_data=PAYMENTS_CB
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
    
    # Format transactions
    transaction_text = get_text("transaction_history_header", language_code)
    transaction_text += "\n\n"
    
    for i, tx in enumerate(transactions, 1):
        status_text = get_text(f"status_{tx.get('status', 'pending')}", language_code)
        tx_type = tx.get("type", "deposit")
        type_text = get_text(f"transaction_type_{tx_type}", language_code)
        
        transaction_text += f"{i}. *{type_text}* - {format_number(tx.get('amount'), language_code)} Toman\n"
        transaction_text += f"   📅 {format_date(tx.get('created_at'), language_code)}\n"
        transaction_text += f"   🔖 ID: `{tx.get('id')}`\n"
        transaction_text += f"   📊 {status_text}\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("back_to_payments", language_code),
                callback_data=PAYMENTS_CB
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=transaction_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SELECTING_ACTION

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

async def notify_admins_new_payment(bot, transaction_id, payment_method, user_id):
    """Notify admins about a new payment."""
    try:
        # Get admin users
        admins = get_all_users(limit=100, offset=0)
        admins = [admin for admin in admins if admin.get("is_admin", False)]
        
        if not admins:
            logger.warning("No admin users found to notify about new payment")
            return
        
        # Get transaction details
        transaction = get_transaction(transaction_id)
        if not transaction:
            logger.error(f"Transaction {transaction_id} not found for admin notification")
            return
        
        # Get user details
        user = get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found for admin notification")
            return
        
        # Create notification message
        method_name = "Card-to-Card" if payment_method == "card" else "Zarinpal"
        
        message = f"🔔 *New {method_name} Payment*\n\n"
        message += f"👤 User: {user.get('username') or user.get('first_name')} (ID: {user_id})\n"
        message += f"💰 Amount: {format_number(transaction.get('amount'), 'fa')} Toman\n"
        message += f"🆔 Transaction ID: `{transaction_id}`\n"
        message += f"⏱ Created at: {format_date(transaction.get('created_at'), 'fa')}\n\n"
        
        if payment_method == "card":
            message += f"📝 Tracking Number: {transaction.get('receipt_number')}\n\n"
        
        message += "Please verify this payment in the admin panel."
        
        # Send notification to all admins
        for admin in admins:
            admin_id = admin.get("user_id")
            if admin_id:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error notifying admins about new payment: {str(e)}")
        return False

def get_payments_handler() -> ConversationHandler:
    """Get the payments conversation handler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(payments_menu, pattern=f"^{PAYMENTS_CB}$")
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(card_payment, pattern=f"^{CARD_PAYMENT}$"),
                CallbackQueryHandler(zarinpal_payment, pattern=f"^{ZARINPAL_PAYMENT}$"),
                CallbackQueryHandler(transaction_history, pattern=f"^{TRANSACTION_HISTORY}$"),
            ],
            SELECTING_METHOD: [
                CallbackQueryHandler(card_payment, pattern=f"^{CARD_PAYMENT}$"),
                CallbackQueryHandler(zarinpal_payment, pattern=f"^{ZARINPAL_PAYMENT}$"),
                CallbackQueryHandler(payments_menu, pattern=f"^{PAYMENTS_CB}$"),
            ],
            ENTERING_AMOUNT: [
                CallbackQueryHandler(process_amount, pattern=f"^{PAYMENTS_CB}_enter_amount$"),
                CallbackQueryHandler(payments_menu, pattern=f"^{PAYMENTS_CB}$"),
                CallbackQueryHandler(card_payment, pattern=f"^{CARD_PAYMENT}$"),
                CallbackQueryHandler(zarinpal_payment, pattern=f"^{ZARINPAL_PAYMENT}$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_amount),
            ],
            CONFIRMING_PAYMENT: [
                CallbackQueryHandler(confirm_payment, pattern=f"^{PAYMENTS_CB}_confirm$"),
                CallbackQueryHandler(cancel_payment, pattern=f"^{CANCEL_PAYMENT}$"),
            ],
            ENTERING_RECEIPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_receipt),
                CallbackQueryHandler(cancel_payment, pattern=f"^{CANCEL_PAYMENT}$"),
            ],
            VERIFYING_PAYMENT: [
                CallbackQueryHandler(verify_zarinpal_payment, pattern=f"^{VERIFY_PAYMENT}$"),
                CallbackQueryHandler(cancel_payment, pattern=f"^{CANCEL_PAYMENT}$"),
                CallbackQueryHandler(payments_menu, pattern=f"^{PAYMENTS_CB}$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_payment, pattern=f"^{CANCEL_PAYMENT}$"),
            CallbackQueryHandler(payments_menu, pattern=f"^{PAYMENTS_CB}$"),
        ],
        name="payments_conversation",
        persistent=False,
    ) 