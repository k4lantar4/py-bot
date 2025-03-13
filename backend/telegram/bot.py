import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import ContextTypes, ConversationHandler, filters
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
import re
from datetime import datetime

from main.models import Server, SubscriptionPlan, Subscription
from v2ray.models import Inbound, Client, SyncLog, ClientConfig
from payments.models import Transaction, CardPayment, ZarinpalPayment, PaymentMethod, Discount
from telegram.models import TelegramMessage, TelegramCallback, TelegramState, TelegramNotification, TelegramLog
from .default_messages import get_default_message

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

User = get_user_model()

# Define conversation states
(
    SELECTING_LANGUAGE, 
    MAIN_MENU, 
    ACCOUNT_MENU,
    PAYMENT_MENU,
    PLAN_SELECTION,
    SERVER_SELECTION,
    PAYMENT_METHOD_SELECTION,
    CARD_PAYMENT_INFO,
    ZARINPAL_PAYMENT,
    SUPPORT_CONVERSATION,
    ADMIN_MENU,
    ADMIN_SERVER_MENU,
    ADMIN_USER_MENU,
    ADMIN_PLAN_MENU,
    ADMIN_PAYMENT_MENU,
    ADMIN_DISCOUNT_MENU
) = range(16)

# Helper function to get message template
def get_message(name, lang='fa'):
    """Get message template by name and language"""
    try:
        message = TelegramMessage.objects.get(name=name, language_code=lang)
        return message.content
    except TelegramMessage.DoesNotExist:
        # Fallback to default messages
        return get_default_message(name, lang)

# Helper function to log bot activity
async def log_activity(user_id=None, level='info', message='', details=None):
    """Log bot activity to database"""
    try:
        user = None
        if user_id:
            try:
                user = User.objects.get(telegram_id=user_id)
            except User.DoesNotExist:
                pass
        
        TelegramLog.objects.create(
            user=user,
            level=level,
            message=message,
            details=details
        )
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a welcome message and initialize the conversation."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Log activity
    await log_activity(user.id, 'info', f"User started the bot: {user.id} - {user.full_name}")
    
    # Check if user exists in the database
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Send main menu directly if user exists
        return await show_main_menu(update, context)
        
    except User.DoesNotExist:
        # User doesn't exist, create a new user
        try:
            new_user = User.objects.create(
                username=f"tg_{user.id}",
                telegram_id=user.id,
                language_code=user.language_code or 'fa',
                is_active=True
            )
            language_code = new_user.language_code
            
            # Store user in context
            context.user_data['user_id'] = new_user.id
            context.user_data['language_code'] = language_code
            
            # Offer language selection
            return await select_language(update, context)
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            await update.message.reply_text("Error creating user account. Please try again later.")
            return ConversationHandler.END

# Language selection handler
async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show language selection buttons."""
    keyboard = [
        [
            InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa"),
            InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = get_message('welcome', 'fa')
    
    if update.message:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup)
    
    return SELECTING_LANGUAGE

# Language selection callback handler
async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle language selection."""
    query = update.callback_query
    await query.answer()
    
    language_code = query.data.split('_')[1]  # Extract language code from callback data
    
    # Update user language preference in database
    user = update.effective_user
    try:
        db_user = User.objects.get(telegram_id=user.id)
        db_user.language_code = language_code
        db_user.save()
        
        # Store in context
        context.user_data['language_code'] = language_code
        
        # Log activity
        await log_activity(user.id, 'info', f"User selected language: {language_code}")
        
        # Show main menu
        return await show_main_menu(update, context)
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        await query.edit_message_text("Error updating language preference. Please try again later.")
        return ConversationHandler.END

# Main menu handler
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the main menu."""
    user = update.effective_user
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Store in context
        context.user_data['user_id'] = db_user.id
        context.user_data['language_code'] = language_code
        
        # Build main menu keyboard
        keyboard = [
            [InlineKeyboardButton(get_message('btn_my_accounts', language_code), callback_data="menu_accounts")],
            [InlineKeyboardButton(get_message('btn_buy_subscription', language_code), callback_data="menu_buy")],
            [InlineKeyboardButton(get_message('btn_payment', language_code), callback_data="menu_payment")],
            [InlineKeyboardButton(get_message('btn_support', language_code), callback_data="menu_support")],
            [InlineKeyboardButton(get_message('btn_profile', language_code), callback_data="menu_profile")],
        ]
        
        # Add admin button if user is admin
        if db_user.is_admin:
            keyboard.append([InlineKeyboardButton(get_message('btn_admin', language_code), callback_data="menu_admin")])
            
        # Add language button
        keyboard.append([InlineKeyboardButton(get_message('btn_language', language_code), callback_data="menu_language")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        main_menu_message = get_message('main_menu', language_code)
        
        if update.message:
            await update.message.reply_text(main_menu_message, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(main_menu_message, reply_markup=reply_markup)
        
        return MAIN_MENU
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        if update.message:
            await update.message.reply_text("Error loading main menu. Please try /start again.")
        else:
            await update.callback_query.edit_message_text("Error loading main menu. Please try /start again.")
        return ConversationHandler.END

# Main menu callback handler
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu button clicks."""
    query = update.callback_query
    await query.answer()
    
    action = query.data.split('_')[1]
    
    if action == "accounts":
        return await show_accounts(update, context)
    elif action == "buy":
        return await show_plans(update, context)
    elif action == "payment":
        return await show_payment_menu(update, context)
    elif action == "support":
        return await start_support_conversation(update, context)
    elif action == "profile":
        return await show_profile(update, context)
    elif action == "admin":
        return await show_admin_menu(update, context)
    elif action == "language":
        return await select_language(update, context)
    else:
        return await show_main_menu(update, context)

# Accounts menu handler
async def show_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's V2Ray accounts."""
    query = update.callback_query
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get active subscriptions
        subscriptions = Subscription.objects.filter(
            user=db_user, 
            status='active'
        ).order_by('-created_at')
        
        if not subscriptions.exists():
            # No active subscriptions
            message = get_message('no_active_accounts', language_code)
            keyboard = [
                [InlineKeyboardButton(get_message('btn_buy_subscription', language_code), callback_data="menu_buy")],
                [InlineKeyboardButton(get_message('btn_back_main', language_code), callback_data="back_main")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            return ACCOUNT_MENU
        
        # Show list of accounts
        keyboard = []
        for subscription in subscriptions:
            btn_text = f"{subscription.plan.name} - {subscription.remaining_days()} روز"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"account_{subscription.id}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton(get_message('btn_back_main', language_code), callback_data="back_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = get_message('accounts_list', language_code)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        return ACCOUNT_MENU
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        await query.edit_message_text("Error loading accounts. Please try /start again.")
        return ConversationHandler.END

# Account details handler
async def show_account_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show details of a specific account."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    subscription_id = int(query.data.split('_')[1])
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get subscription
        subscription = Subscription.objects.get(id=subscription_id, user=db_user)
        
        # Get client config
        try:
            client = Client.objects.get(email=subscription.client_email, inbound__server=subscription.server)
            client_config = ClientConfig.objects.get(client=client)
            
            # Build message with account details
            message = get_message('account_details', language_code).format(
                plan_name=subscription.plan.name,
                server_name=subscription.server.name,
                remaining_days=subscription.remaining_days(),
                expiry_date=subscription.end_date.strftime("%Y-%m-%d"),
                data_usage=f"{subscription.data_usage_gb:.2f} GB",
                data_limit=f"{subscription.data_limit_gb} GB" if subscription.data_limit_gb > 0 else get_message('unlimited', language_code),
                usage_percentage=f"{subscription.data_usage_percentage():.1f}%"
            )
            
            # Build keyboard for config links
            keyboard = []
            
            # Add config links based on protocol
            if client_config.vmess_link:
                keyboard.append([InlineKeyboardButton(get_message('btn_vmess_config', language_code), callback_data=f"config_vmess_{subscription_id}")])
            
            if client_config.vless_link:
                keyboard.append([InlineKeyboardButton(get_message('btn_vless_config', language_code), callback_data=f"config_vless_{subscription_id}")])
                
            if client_config.trojan_link:
                keyboard.append([InlineKeyboardButton(get_message('btn_trojan_config', language_code), callback_data=f"config_trojan_{subscription_id}")])
                
            if client_config.shadowsocks_link:
                keyboard.append([InlineKeyboardButton(get_message('btn_shadowsocks_config', language_code), callback_data=f"config_shadowsocks_{subscription_id}")])
            
            if client_config.subscription_url:
                keyboard.append([InlineKeyboardButton(get_message('btn_subscription_url', language_code), callback_data=f"config_subscription_{subscription_id}")])
            
            if client_config.qrcode_data:
                keyboard.append([InlineKeyboardButton(get_message('btn_qrcode', language_code), callback_data=f"config_qrcode_{subscription_id}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton(get_message('btn_back_accounts', language_code), callback_data="back_accounts")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            
        except (Client.DoesNotExist, ClientConfig.DoesNotExist):
            # Config not found
            message = get_message('config_not_found', language_code)
            keyboard = [
                [InlineKeyboardButton(get_message('btn_back_accounts', language_code), callback_data="back_accounts")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
        
        return ACCOUNT_MENU
        
    except (User.DoesNotExist, Subscription.DoesNotExist):
        logger.error(f"User or subscription not found for telegram_id: {user.id}, subscription_id: {subscription_id}")
        await query.edit_message_text("Error loading account details. Please try /start again.")
        return ConversationHandler.END

# Config link handler
async def show_config_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show configuration link for the account."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    parts = query.data.split('_')
    config_type = parts[1]
    subscription_id = int(parts[2])
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get subscription
        subscription = Subscription.objects.get(id=subscription_id, user=db_user)
        
        # Get client config
        try:
            client = Client.objects.get(email=subscription.client_email, inbound__server=subscription.server)
            client_config = ClientConfig.objects.get(client=client)
            
            # Get config link based on type
            config_link = ""
            if config_type == "vmess":
                config_link = client_config.vmess_link
            elif config_type == "vless":
                config_link = client_config.vless_link
            elif config_type == "trojan":
                config_link = client_config.trojan_link
            elif config_type == "shadowsocks":
                config_link = client_config.shadowsocks_link
            elif config_type == "subscription":
                config_link = client_config.subscription_url
            elif config_type == "qrcode":
                # Send QR code image
                # This would require generating and sending the QR code image
                await query.message.reply_text(get_message('qrcode_coming_soon', language_code))
                return ACCOUNT_MENU
            
            if not config_link:
                await query.message.reply_text(get_message('config_not_available', language_code))
                return ACCOUNT_MENU
            
            # Send config link
            config_message = get_message('config_link', language_code).format(
                plan_name=subscription.plan.name,
                server_name=subscription.server.name,
                config_type=config_type.upper()
            )
            
            await query.message.reply_text(f"{config_message}\n\n`{config_link}`", parse_mode="Markdown")
            
        except (Client.DoesNotExist, ClientConfig.DoesNotExist):
            # Config not found
            await query.message.reply_text(get_message('config_not_found', language_code))
        
        return ACCOUNT_MENU
        
    except (User.DoesNotExist, Subscription.DoesNotExist):
        logger.error(f"User or subscription not found for telegram_id: {user.id}, subscription_id: {subscription_id}")
        await query.message.reply_text("Error getting configuration. Please try /start again.")
        return ConversationHandler.END

# Show plans handler
async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available subscription plans."""
    query = update.callback_query
    if query:
        await query.answer()
    
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get active plans
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
        
        if not plans.exists():
            # No active plans
            message = get_message('no_active_plans', language_code)
            keyboard = [
                [InlineKeyboardButton(get_message('btn_back_main', language_code), callback_data="back_main")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if query:
                await query.edit_message_text(message, reply_markup=reply_markup)
            else:
                await update.message.reply_text(message, reply_markup=reply_markup)
                
            return MAIN_MENU
        
        # Show list of plans
        message = get_message('plans_list', language_code)
        keyboard = []
        
        for plan in plans:
            plan_features = []
            if plan.data_limit_gb > 0:
                plan_features.append(f"{plan.data_limit_gb} GB")
            else:
                plan_features.append(get_message('unlimited_traffic', language_code))
            
            plan_features.append(f"{plan.duration_days} {get_message('days', language_code)}")
            
            btn_text = f"{plan.name} ({', '.join(plan_features)}) - {plan.price} {get_message('currency', language_code)}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"plan_{plan.id}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton(get_message('btn_back_main', language_code), callback_data="back_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
            
        return PLAN_SELECTION
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        message = "Error loading plans. Please try /start again."
        
        if query:
            await query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
            
        return ConversationHandler.END

# Helper functions for back actions
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Go back to main menu."""
    return await show_main_menu(update, context)

async def back_to_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Go back to accounts menu."""
    return await show_accounts(update, context)

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    user = update.effective_user
    await log_activity(user.id, 'info', f"User cancelled conversation: {user.id} - {user.full_name}")
    
    await update.message.reply_text("Operation cancelled. Type /start to begin again.")
    return ConversationHandler.END

# Help handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message."""
    user = update.effective_user
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        help_message = get_message('help', language_code)
        await update.message.reply_text(help_message)
        
    except User.DoesNotExist:
        # Default help message in English and Persian
        help_message = """
*Help*
- /start: Start or restart the bot
- /help: Show this help message
- /language: Change language
- /cancel: Cancel current operation

*راهنما*
- /start: شروع یا راه‌اندازی مجدد ربات
- /help: نمایش این پیام راهنما
- /language: تغییر زبان
- /cancel: لغو عملیات فعلی
"""
        await update.message.reply_text(help_message, parse_mode="Markdown")

# Language command handler
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Change language."""
    return await select_language(update, context)

# Profile handler
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user profile information."""
    query = update.callback_query
    if query:
        await query.answer()
    
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Format user information
        language_name = "فارسی" if language_code == 'fa' else "English"
        
        profile_message = get_message('profile_info', language_code).format(
            username=db_user.username,
            wallet_balance=f"{db_user.wallet_balance:,}",
            date_joined=db_user.date_joined.strftime("%Y-%m-%d"),
            language=language_name
        )
        
        # Build keyboard
        keyboard = [
            [InlineKeyboardButton(get_message('btn_recharge_wallet', language_code), callback_data="profile_recharge")],
            [InlineKeyboardButton(get_message('btn_language', language_code), callback_data="menu_language")],
            [InlineKeyboardButton(get_message('btn_back_main', language_code), callback_data="back_main")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(profile_message, parse_mode="Markdown", reply_markup=reply_markup)
        else:
            await update.message.reply_text(profile_message, parse_mode="Markdown", reply_markup=reply_markup)
        
        return MAIN_MENU
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        message = get_message('error_user_not_found', 'fa')
        
        if query:
            await query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
            
        return ConversationHandler.END

# Support conversation handler
async def start_support_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start support conversation."""
    query = update.callback_query
    if query:
        await query.answer()
    
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        support_message = get_message('support_message', language_code)
        
        # Set state for support conversation
        context.user_data['support_state'] = True
        
        # Keyboard with cancel button
        keyboard = [
            [InlineKeyboardButton(get_message('btn_back_main', language_code), callback_data="back_main")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(support_message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(support_message, reply_markup=reply_markup)
        
        return SUPPORT_CONVERSATION
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        message = get_message('error_user_not_found', 'fa')
        
        if query:
            await query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
            
        return ConversationHandler.END

# Handle support messages
async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle support messages from users."""
    message_text = update.message.text
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Log support message
        await log_activity(
            user.id, 
            'info', 
            f"Support message from {user.id} - {user.full_name}",
            {'message': message_text}
        )
        
        # Create notification for admins
        admin_notification = f"📩 پیام پشتیبانی جدید از {db_user.username}:\n\n{message_text}"
        
        # Create notification for admin users
        admin_users = User.objects.filter(is_admin=True)
        for admin in admin_users:
            if admin.telegram_id:
                TelegramNotification.objects.create(
                    user=admin,
                    type='admin',
                    message=admin_notification,
                    status='pending'
                )
        
        # Send confirmation to user
        success_message = get_message('support_sent', language_code)
        await update.message.reply_text(success_message)
        
        # Return to main menu
        await show_main_menu(update, context)
        return MAIN_MENU
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        message = get_message('error_user_not_found', 'fa')
        await update.message.reply_text(message)
        return ConversationHandler.END

# Show payment menu
async def show_payment_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show payment menu."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        payment_message = get_message('payment_menu', language_code)
        
        # Build keyboard
        keyboard = [
            [InlineKeyboardButton(get_message('btn_recharge_wallet', language_code), callback_data="payment_recharge")],
            [InlineKeyboardButton(get_message('btn_payment_history', language_code), callback_data="payment_history")],
            [InlineKeyboardButton(get_message('btn_check_payment', language_code), callback_data="payment_check")],
            [InlineKeyboardButton(get_message('btn_back_main', language_code), callback_data="back_main")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(payment_message, reply_markup=reply_markup)
        
        return PAYMENT_MENU
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        await query.edit_message_text(get_message('error_user_not_found', 'fa'))
        return ConversationHandler.END

# Payment menu callback handler
async def handle_payment_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment menu button clicks."""
    query = update.callback_query
    await query.answer()
    
    action = query.data.split('_')[1]
    
    if action == "recharge":
        return await start_wallet_recharge(update, context)
    elif action == "history":
        return await show_payment_history(update, context)
    elif action == "check":
        return await start_payment_check(update, context)
    else:
        return await show_payment_menu(update, context)

# Start wallet recharge process
async def start_wallet_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start wallet recharge process."""
    query = update.callback_query
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get active payment methods
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        
        if not payment_methods.exists():
            # No active payment methods
            message = get_message('no_payment_methods', language_code)
            keyboard = [
                [InlineKeyboardButton(get_message('btn_back_payment', language_code), callback_data="back_payment")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            return PAYMENT_MENU
        
        # Show payment methods
        message = get_message('select_payment_method', language_code)
        keyboard = []
        
        for method in payment_methods:
            keyboard.append([InlineKeyboardButton(method.name, callback_data=f"paymethod_{method.id}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton(get_message('btn_back_payment', language_code), callback_data="back_payment")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
        
        return PAYMENT_METHOD_SELECTION
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        await query.edit_message_text(get_message('error_user_not_found', 'fa'))
        return ConversationHandler.END

# Payment method selection handler
async def select_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment method selection."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    method_id = int(query.data.split('_')[1])
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get payment method
        payment_method = PaymentMethod.objects.get(id=method_id)
        
        # Store selected method in context
        context.user_data['payment_method_id'] = method_id
        context.user_data['payment_method_type'] = payment_method.type
        
        if payment_method.type == 'card':
            # Card payment - ask for amount
            message = get_message('enter_payment_amount', language_code)
            
            # Add instructions if available
            if payment_method.instructions:
                message += f"\n\n{payment_method.instructions}"
            
            # Add back button
            keyboard = [
                [InlineKeyboardButton(get_message('btn_back_payment', language_code), callback_data="back_payment")],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            
            # Set state for waiting for amount
            context.user_data['payment_state'] = 'waiting_amount'
            
            return CARD_PAYMENT_INFO
            
        elif payment_method.type == 'zarinpal':
            # Zarinpal payment - implement later
            message = get_message('zarinpal_coming_soon', language_code)
            keyboard = [
                [InlineKeyboardButton(get_message('btn_back_payment', language_code), callback_data="back_payment")],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            
            return PAYMENT_MENU
            
    except (User.DoesNotExist, PaymentMethod.DoesNotExist):
        logger.error(f"User or payment method not found for telegram_id: {user.id}, method_id: {method_id}")
        await query.edit_message_text(get_message('error_general', 'fa'))
        return ConversationHandler.END

# Handle card payment amount
async def handle_card_payment_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle card payment amount input."""
    message_text = update.message.text
    user = update.effective_user
    
    try:
        # Try to parse amount
        try:
            amount = float(message_text.replace(',', '').strip())
        except ValueError:
            # Invalid amount
            await update.message.reply_text(get_message('invalid_amount', 'fa'))
            return CARD_PAYMENT_INFO
        
        # Check amount is valid
        if amount <= 0:
            await update.message.reply_text(get_message('invalid_amount', 'fa'))
            return CARD_PAYMENT_INFO
        
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Store amount in context
        context.user_data['payment_amount'] = amount
        
        # Get payment method
        method_id = context.user_data.get('payment_method_id')
        payment_method = PaymentMethod.objects.get(id=method_id)
        
        # Get card information from payment method
        extra_data = payment_method.extra_data or {}
        card_number = extra_data.get('card_number', settings.CARD_NUMBER)
        card_holder = extra_data.get('card_holder', settings.CARD_HOLDER)
        
        # Show card information and ask for transfer details
        message = get_message('card_payment_info', language_code).format(
            amount=f"{amount:,}",
            card_number=card_number,
            card_holder=card_holder
        )
        
        # Update payment state
        context.user_data['payment_state'] = 'waiting_card_number'
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
        # Ask for card number
        await update.message.reply_text(get_message('enter_card_number', language_code))
        
        return CARD_PAYMENT_INFO
        
    except (User.DoesNotExist, PaymentMethod.DoesNotExist):
        logger.error(f"Error processing payment amount for user: {user.id}")
        await update.message.reply_text(get_message('error_general', 'fa'))
        return ConversationHandler.END

# Handle card number input
async def handle_card_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle card number input."""
    message_text = update.message.text
    user = update.effective_user
    
    # Check card number format (simple validation)
    card_number = re.sub(r'\s+', '', message_text)
    if not card_number.isdigit() or len(card_number) != 16:
        await update.message.reply_text(get_message('invalid_card_number', 'fa'))
        return CARD_PAYMENT_INFO
    
    # Store card number in context
    context.user_data['card_number'] = card_number
    
    # Update payment state
    context.user_data['payment_state'] = 'waiting_reference'
    
    # Ask for reference number
    await update.message.reply_text(get_message('enter_reference_number', 'fa'))
    
    return CARD_PAYMENT_INFO

# Handle reference number input
async def handle_reference_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle reference number input."""
    message_text = update.message.text
    user = update.effective_user
    
    # Simple validation for reference number
    reference_number = message_text.strip()
    if not reference_number:
        await update.message.reply_text(get_message('invalid_reference', 'fa'))
        return CARD_PAYMENT_INFO
    
    # Store reference number in context
    context.user_data['reference_number'] = reference_number
    
    # Update payment state
    context.user_data['payment_state'] = 'waiting_date'
    
    # Ask for transfer date and time
    await update.message.reply_text(get_message('enter_transfer_time', 'fa'))
    
    return CARD_PAYMENT_INFO

# Handle transfer time input
async def handle_transfer_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle transfer time input."""
    message_text = update.message.text
    user = update.effective_user
    
    try:
        # Try to parse transfer time (simple format: YYYY-MM-DD HH:MM)
        try:
            transfer_time = datetime.strptime(message_text.strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            # Try alternative formats
            try:
                transfer_time = datetime.strptime(message_text.strip(), "%Y/%m/%d %H:%M")
            except ValueError:
                await update.message.reply_text(get_message('invalid_date_format', 'fa'))
                return CARD_PAYMENT_INFO
        
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get payment data from context
        payment_amount = context.user_data.get('payment_amount')
        card_number = context.user_data.get('card_number')
        reference_number = context.user_data.get('reference_number')
        
        # Create transaction
        with transaction.atomic():
            # Create transaction record
            tx = Transaction.objects.create(
                user=db_user,
                amount=payment_amount,
                status='pending',
                type='deposit',
                description='Card payment deposit'
            )
            
            # Create card payment record
            from payments.card_payment import CardPaymentProcessor
            processor = CardPaymentProcessor()
            result = processor.create_payment(
                tx.id,
                card_number,
                reference_number,
                transfer_time
            )
            
            if not result.get('success'):
                # Payment creation failed
                logger.error(f"Error creating card payment: {result.get('error_message')}")
                await update.message.reply_text(get_message('payment_creation_failed', language_code))
                return ConversationHandler.END
            
            # Payment created successfully
            verification_code = result.get('verification_code')
            
            # Send confirmation message
            message = get_message('payment_created', language_code).format(
                amount=f"{payment_amount:,}",
                verification_code=verification_code
            )
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
            # Clear payment data from context
            context.user_data.pop('payment_state', None)
            context.user_data.pop('payment_method_id', None)
            context.user_data.pop('payment_method_type', None)
            context.user_data.pop('payment_amount', None)
            context.user_data.pop('card_number', None)
            context.user_data.pop('reference_number', None)
            
            # Return to main menu
            return await show_main_menu(update, context)
        
    except Exception as e:
        logger.error(f"Error processing card payment: {str(e)}")
        await update.message.reply_text(get_message('error_general', 'fa'))
        return ConversationHandler.END

# Handle card payment information
async def handle_card_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle card payment information input."""
    # Check which state we're in and call the appropriate handler
    payment_state = context.user_data.get('payment_state')
    
    if payment_state == 'waiting_amount':
        return await handle_card_payment_amount(update, context)
    elif payment_state == 'waiting_card_number':
        return await handle_card_number(update, context)
    elif payment_state == 'waiting_reference':
        return await handle_reference_number(update, context)
    elif payment_state == 'waiting_date':
        return await handle_transfer_time(update, context)
    else:
        # Unknown state, go back to payment menu
        return await show_payment_menu(update, context)

# Show payment history
async def show_payment_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's payment history."""
    query = update.callback_query
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get recent transactions
        transactions = Transaction.objects.filter(user=db_user).order_by('-created_at')[:10]
        
        if not transactions.exists():
            # No transactions
            message = get_message('no_payment_history', language_code)
            keyboard = [
                [InlineKeyboardButton(get_message('btn_back_payment', language_code), callback_data="back_payment")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            return PAYMENT_MENU
        
        # Build payment history message
        message = get_message('payment_history', language_code) + "\n\n"
        
        for tx in transactions:
            # Format transaction info
            status_text = get_message(f'status_{tx.status}', language_code)
            type_text = get_message(f'type_{tx.type}', language_code)
            date_text = tx.created_at.strftime("%Y-%m-%d %H:%M")
            
            message += get_message('payment_history_item', language_code).format(
                id=tx.id,
                amount=f"{tx.amount:,}",
                status=status_text,
                type=type_text,
                date=date_text
            ) + "\n\n"
        
        # Add back button
        keyboard = [
            [InlineKeyboardButton(get_message('btn_back_payment', language_code), callback_data="back_payment")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
        
        return PAYMENT_MENU
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        await query.edit_message_text(get_message('error_user_not_found', 'fa'))
        return ConversationHandler.END

# Start payment check process
async def start_payment_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start payment check process."""
    query = update.callback_query
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Ask for verification code
        message = get_message('enter_verification_code', language_code)
        
        # Set state for waiting for verification code
        context.user_data['payment_state'] = 'checking_payment'
        
        # Add back button
        keyboard = [
            [InlineKeyboardButton(get_message('btn_back_payment', language_code), callback_data="back_payment")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
        
        return PAYMENT_MENU
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        await query.edit_message_text(get_message('error_user_not_found', 'fa'))
        return ConversationHandler.END

# Handle payment check
async def handle_payment_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment check."""
    message_text = update.message.text
    user = update.effective_user
    
    try:
        db_user = User.objects.get(telegram_id=user.id)
        language_code = db_user.language_code
        
        # Get verification code
        verification_code = message_text.strip()
        
        # Check payment status
        try:
            card_payment = CardPayment.objects.get(verification_code=verification_code)
            tx = card_payment.transaction
            
            # Check user owns this payment
            if tx.user.id != db_user.id:
                await update.message.reply_text(get_message('payment_not_found', language_code))
                return PAYMENT_MENU
            
            # Get payment status
            status_text = get_message(f'status_{tx.status}', language_code)
            card_status_text = get_message(f'status_{card_payment.status}', language_code)
            
            # Format payment info
            message = get_message('payment_info', language_code).format(
                amount=f"{tx.amount:,}",
                status=status_text,
                card_status=card_status_text,
                date=tx.created_at.strftime("%Y-%m-%d %H:%M"),
                card_number=card_payment.card_number,
                reference=card_payment.reference_number
            )
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
            # Clear payment state
            context.user_data.pop('payment_state', None)
            
            # Return to main menu
            return await show_main_menu(update, context)
            
        except CardPayment.DoesNotExist:
            await update.message.reply_text(get_message('payment_not_found', language_code))
            return PAYMENT_MENU
        
    except User.DoesNotExist:
        logger.error(f"User not found for telegram_id: {user.id}")
        await update.message.reply_text(get_message('error_user_not_found', 'fa'))
        return ConversationHandler.END

# Helper functions for back actions
async def back_to_payment_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Go back to payment menu."""
    return await show_payment_menu(update, context)

# Setup function
def setup_bot():
    """Set up and return the bot application."""
    # Get bot token from settings
    token = settings.TELEGRAM_BOT_TOKEN
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("language", language_command),
        ],
        states={
            SELECTING_LANGUAGE: [
                CallbackQueryHandler(language_selection, pattern=r"^lang_"),
            ],
            MAIN_MENU: [
                CallbackQueryHandler(handle_main_menu, pattern=r"^menu_"),
                CallbackQueryHandler(back_to_main_menu, pattern=r"^back_main$"),
            ],
            ACCOUNT_MENU: [
                CallbackQueryHandler(show_account_details, pattern=r"^account_"),
                CallbackQueryHandler(show_config_link, pattern=r"^config_"),
                CallbackQueryHandler(back_to_accounts, pattern=r"^back_accounts$"),
                CallbackQueryHandler(back_to_main_menu, pattern=r"^back_main$"),
            ],
            PLAN_SELECTION: [
                # Will be implemented later
                CallbackQueryHandler(back_to_main_menu, pattern=r"^back_main$"),
            ],
            PAYMENT_MENU: [
                CallbackQueryHandler(handle_payment_menu, pattern=r"^payment_"),
                CallbackQueryHandler(back_to_main_menu, pattern=r"^back_main$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_check),
            ],
            PAYMENT_METHOD_SELECTION: [
                CallbackQueryHandler(select_payment_method, pattern=r"^paymethod_"),
                CallbackQueryHandler(back_to_payment_menu, pattern=r"^back_payment$"),
            ],
            CARD_PAYMENT_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_card_payment_info),
                CallbackQueryHandler(back_to_payment_menu, pattern=r"^back_payment$"),
            ],
            SUPPORT_CONVERSATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_message),
                CallbackQueryHandler(back_to_main_menu, pattern=r"^back_main$"),
            ],
            # Other states will be implemented later
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    return application

# Function to run the bot
def run_bot():
    """Run the bot."""
    application = setup_bot()
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# Run the bot if this file is executed directly
if __name__ == "__main__":
    run_bot() 