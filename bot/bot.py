#!/usr/bin/env python3
"""
Telegram Bot for the 3X-UI Management System.

This module implements a Telegram bot that mirrors the functionality
of the web interface, allowing users to manage their accounts, view
server status, and perform other actions.
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
import asyncio

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode
import emoji

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("telegram_bot")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
    sys.exit(1)

# Admin user IDs (users who can access admin commands)
ADMIN_USER_IDS = json.loads(os.getenv("ADMIN_USER_IDS", "[]"))

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# HTTP client for API requests
http_client = httpx.AsyncClient(timeout=30.0)

# User session storage (user_id -> token)
user_sessions: Dict[int, Dict[str, Any]] = {}


# Helper functions
async def api_request(
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Make a request to the API.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint
        token: JWT token for authentication
        data: Request data
        params: Query parameters
        
    Returns:
        API response as dictionary
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = await http_client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await http_client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = await http_client.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = await http_client.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"API request error: {e.response.status_code} - {e.response.text}")
        try:
            return e.response.json()
        except:
            return {"detail": f"Error: {e}"}
    except Exception as e:
        logger.error(f"API request exception: {e}")
        return {"detail": f"Error: {e}"}


async def is_admin(user_id: int) -> bool:
    """
    Check if a user is an admin.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if the user is an admin, False otherwise
    """
    return user_id in ADMIN_USER_IDS


async def is_authenticated(user_id: int) -> bool:
    """
    Check if a user is authenticated.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if the user is authenticated, False otherwise
    """
    return user_id in user_sessions and "access_token" in user_sessions[user_id]


def admin_required(func: Callable) -> Callable:
    """
    Decorator to require admin privileges for a command.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user_id = update.effective_user.id
        if not await is_admin(user_id):
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
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user_id = update.effective_user.id
        if not await is_authenticated(user_id):
            await update.message.reply_text(
                f"{emoji.emojize(':locked:')} You need to log in first. Use /login to authenticate."
            )
            return
        return await func(update, context)
    return wrapper


# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    """
    user = update.effective_user
    await update.message.reply_html(
        f"{emoji.emojize(':rocket:')} Hi {user.mention_html()}!\n\n"
        f"Welcome to the 3X-UI Management Bot. This bot allows you to manage your 3X-UI services.\n\n"
        f"Use /help to see available commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    """
    user_id = update.effective_user.id
    is_user_admin = await is_admin(user_id)
    is_user_authenticated = await is_authenticated(user_id)
    
    help_text = f"{emoji.emojize(':information:')} Available commands:\n\n"
    
    # Basic commands
    help_text += "/start - Start the bot\n"
    help_text += "/help - Show this help message\n"
    
    # Authentication commands
    if is_user_authenticated:
        help_text += "/logout - Log out from your account\n"
        help_text += "/profile - View your profile information\n"
    else:
        help_text += "/login - Log in to your account\n"
    
    # User commands (require authentication)
    if is_user_authenticated:
        help_text += "/services - List available services\n"
        help_text += "/orders - List your orders\n"
        help_text += "/clients - List your clients\n"
        help_text += "/status - Check server status\n"
    
    # Admin commands
    if is_user_admin:
        help_text += "\n" + emoji.emojize(':star:') + " Admin commands:\n"
        help_text += "/users - List users\n"
        help_text += "/servers - List servers\n"
        help_text += "/locations - List locations\n"
        help_text += "/stats - Show system statistics\n"
    
    await update.message.reply_text(help_text)


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /login command.
    """
    user_id = update.effective_user.id
    
    # Check if already logged in
    if await is_authenticated(user_id):
        await update.message.reply_text(
            f"{emoji.emojize(':check_mark:')} You are already logged in. Use /logout to log out first."
        )
        return
    
    # Ask for email
    await update.message.reply_text(
        f"{emoji.emojize(':envelope:')} Please enter your email address:"
    )
    
    # Store the current state
    context.user_data["login_state"] = "waiting_for_email"


async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /logout command.
    """
    user_id = update.effective_user.id
    
    # Check if logged in
    if not await is_authenticated(user_id):
        await update.message.reply_text(
            f"{emoji.emojize(':information:')} You are not logged in."
        )
        return
    
    # Clear session
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    await update.message.reply_text(
        f"{emoji.emojize(':check_mark:')} You have been logged out successfully."
    )


@auth_required
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /profile command.
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get user profile from API
    response = await api_request("GET", "/users/me", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    # Format profile information
    profile_text = f"{emoji.emojize(':bust_in_silhouette:')} *Your Profile*\n\n"
    profile_text += f"*Username:* {response.get('username', 'N/A')}\n"
    profile_text += f"*Email:* {response.get('email', 'N/A')}\n"
    profile_text += f"*Full Name:* {response.get('full_name', 'N/A')}\n"
    profile_text += f"*Wallet Balance:* ${response.get('wallet_balance', 0):.2f}\n"
    profile_text += f"*Roles:* {', '.join(response.get('roles', ['Customer']))}\n"
    profile_text += f"*Active:* {'Yes' if response.get('is_active', False) else 'No'}\n"
    
    await update.message.reply_text(
        profile_text,
        parse_mode=ParseMode.MARKDOWN
    )


@auth_required
async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /services command.
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get services from API
    response = await api_request("GET", "/services", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    if not response:
        await update.message.reply_text(
            f"{emoji.emojize(':information:')} No services available."
        )
        return
    
    # Format services information
    services_text = f"{emoji.emojize(':package:')} *Available Services*\n\n"
    
    for service in response:
        services_text += f"*{service.get('name', 'Unknown')}*\n"
        services_text += f"Protocol: {service.get('protocol', 'N/A')}\n"
        services_text += f"Price: ${service.get('price', 0):.2f}\n"
        services_text += f"Traffic: {service.get('traffic', 0)} GB\n"
        services_text += f"Duration: {service.get('duration', 0)} days\n"
        services_text += f"Server: {service.get('server_name', 'N/A')}\n\n"
    
    await update.message.reply_text(
        services_text,
        parse_mode=ParseMode.MARKDOWN
    )


@auth_required
async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /orders command.
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get orders from API
    response = await api_request("GET", "/orders/my-orders", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    if not response:
        await update.message.reply_text(
            f"{emoji.emojize(':information:')} You don't have any orders."
        )
        return
    
    # Format orders information
    orders_text = f"{emoji.emojize(':shopping_cart:')} *Your Orders*\n\n"
    
    for order in response:
        status_emoji = {
            "pending": ":hourglass_not_done:",
            "paid": ":check_mark:",
            "completed": ":check_mark_button:",
            "cancelled": ":cross_mark:",
            "failed": ":cross_mark:",
        }.get(order.get("status", ""), ":question_mark:")
        
        orders_text += f"*Order #{order.get('order_number', 'Unknown')}*\n"
        orders_text += f"Service: {order.get('service_name', 'N/A')}\n"
        orders_text += f"Amount: ${order.get('final_amount', 0):.2f}\n"
        orders_text += f"Status: {emoji.emojize(status_emoji)} {order.get('status', 'N/A')}\n"
        orders_text += f"Date: {order.get('created_at', 'N/A')[:10]}\n\n"
    
    await update.message.reply_text(
        orders_text,
        parse_mode=ParseMode.MARKDOWN
    )


@auth_required
async def clients_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /clients command.
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get clients from API
    response = await api_request("GET", "/users/me/clients", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    if not response:
        await update.message.reply_text(
            f"{emoji.emojize(':information:')} You don't have any clients."
        )
        return
    
    # Format clients information
    clients_text = f"{emoji.emojize(':busts_in_silhouette:')} *Your Clients*\n\n"
    
    for client in response:
        status_emoji = ":green_circle:" if client.get("is_active", False) else ":red_circle:"
        
        clients_text += f"*{client.get('email', 'Unknown')}*\n"
        clients_text += f"Service: {client.get('service_name', 'N/A')}\n"
        clients_text += f"Traffic: {client.get('used_traffic', 0)}/{client.get('total_traffic', 0)} GB\n"
        clients_text += f"Status: {emoji.emojize(status_emoji)} {'Active' if client.get('is_active', False) else 'Inactive'}\n"
        
        if client.get("expiry_date"):
            clients_text += f"Expires: {client.get('expiry_date', 'N/A')[:10]}\n"
        
        clients_text += "\n"
    
    await update.message.reply_text(
        clients_text,
        parse_mode=ParseMode.MARKDOWN
    )


@auth_required
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /status command.
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get server status from API
    response = await api_request("GET", "/servers/status", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    if not response:
        await update.message.reply_text(
            f"{emoji.emojize(':information:')} No server status information available."
        )
        return
    
    # Format status information
    status_text = f"{emoji.emojize(':desktop_computer:')} *Server Status*\n\n"
    
    for server_id, status in response.items():
        server_name = status.get("server_name", f"Server {server_id}")
        is_online = status.get("is_online", False)
        status_emoji = ":green_circle:" if is_online else ":red_circle:"
        
        status_text += f"*{server_name}*: {emoji.emojize(status_emoji)} {'Online' if is_online else 'Offline'}\n"
        
        if is_online and "response_time" in status:
            status_text += f"Response Time: {status['response_time']:.2f}s\n"
        
        status_text += "\n"
    
    await update.message.reply_text(
        status_text,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_required
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /users command (admin only).
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get users from API
    response = await api_request("GET", "/users", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    if not response:
        await update.message.reply_text(
            f"{emoji.emojize(':information:')} No users found."
        )
        return
    
    # Format users information
    users_text = f"{emoji.emojize(':busts_in_silhouette:')} *Users*\n\n"
    
    for user in response:
        status_emoji = ":green_circle:" if user.get("is_active", False) else ":red_circle:"
        
        users_text += f"*{user.get('username', 'Unknown')}*\n"
        users_text += f"Email: {user.get('email', 'N/A')}\n"
        users_text += f"Status: {emoji.emojize(status_emoji)} {'Active' if user.get('is_active', False) else 'Inactive'}\n"
        users_text += f"Roles: {', '.join(user.get('roles', ['Customer']))}\n\n"
    
    await update.message.reply_text(
        users_text,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_required
async def servers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /servers command (admin only).
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get servers from API
    response = await api_request("GET", "/servers", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    if not response:
        await update.message.reply_text(
            f"{emoji.emojize(':information:')} No servers found."
        )
        return
    
    # Format servers information
    servers_text = f"{emoji.emojize(':desktop_computer:')} *Servers*\n\n"
    
    for server in response:
        status_emoji = ":green_circle:" if server.get("is_active", False) else ":red_circle:"
        
        servers_text += f"*{server.get('name', 'Unknown')}*\n"
        servers_text += f"Address: {server.get('address', 'N/A')}\n"
        servers_text += f"Location: {server.get('location_name', 'N/A')}\n"
        servers_text += f"Status: {emoji.emojize(status_emoji)} {'Active' if server.get('is_active', False) else 'Inactive'}\n"
        servers_text += f"Bandwidth: {server.get('used_bandwidth', 0)}/{server.get('total_bandwidth', 0)} GB\n\n"
    
    await update.message.reply_text(
        servers_text,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_required
async def locations_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /locations command (admin only).
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get locations from API
    response = await api_request("GET", "/locations", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    if not response:
        await update.message.reply_text(
            f"{emoji.emojize(':information:')} No locations found."
        )
        return
    
    # Format locations information
    locations_text = f"{emoji.emojize(':world_map:')} *Locations*\n\n"
    
    for location in response:
        status_emoji = ":green_circle:" if location.get("is_active", False) else ":red_circle:"
        flag = location.get("flag_emoji", "")
        
        locations_text += f"*{location.get('name', 'Unknown')}* {flag}\n"
        locations_text += f"Country: {location.get('country', 'N/A')} ({location.get('country_code', 'N/A')})\n"
        locations_text += f"Status: {emoji.emojize(status_emoji)} {'Active' if location.get('is_active', False) else 'Inactive'}\n"
        locations_text += f"Servers: {location.get('server_count', 0)}\n\n"
    
    await update.message.reply_text(
        locations_text,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_required
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /stats command (admin only).
    """
    user_id = update.effective_user.id
    token = user_sessions[user_id]["access_token"]
    
    # Get statistics from API
    response = await api_request("GET", "/stats", token=token)
    
    if "detail" in response:
        await update.message.reply_text(
            f"{emoji.emojize(':cross_mark:')} Error: {response['detail']}"
        )
        return
    
    # Format statistics information
    stats_text = f"{emoji.emojize(':bar_chart:')} *System Statistics*\n\n"
    
    # Users stats
    users_stats = response.get("users", {})
    stats_text += f"*Users*\n"
    stats_text += f"Total: {users_stats.get('total', 0)}\n"
    stats_text += f"Active: {users_stats.get('active', 0)}\n\n"
    
    # Servers stats
    servers_stats = response.get("servers", {})
    stats_text += f"*Servers*\n"
    stats_text += f"Total: {servers_stats.get('total', 0)}\n"
    stats_text += f"Online: {servers_stats.get('online', 0)}\n\n"
    
    # Orders stats
    orders_stats = response.get("orders", {})
    stats_text += f"*Orders*\n"
    stats_text += f"Total: {orders_stats.get('total', 0)}\n"
    stats_text += f"Completed: {orders_stats.get('completed', 0)}\n"
    stats_text += f"Revenue: ${orders_stats.get('revenue', 0):.2f}\n"
    
    await update.message.reply_text(
        stats_text,
        parse_mode=ParseMode.MARKDOWN
    )


# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle incoming messages.
    """
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check if we're in a login flow
    if "login_state" in context.user_data:
        login_state = context.user_data["login_state"]
        
        if login_state == "waiting_for_email":
            # Store email and ask for password
            context.user_data["login_email"] = text
            context.user_data["login_state"] = "waiting_for_password"
            
            await update.message.reply_text(
                f"{emoji.emojize(':locked:')} Please enter your password:"
            )
            return
        
        elif login_state == "waiting_for_password":
            # Attempt login
            email = context.user_data.get("login_email", "")
            password = text
            
            # Clear login state
            del context.user_data["login_state"]
            if "login_email" in context.user_data:
                del context.user_data["login_email"]
            
            # Call login API
            response = await api_request(
                "POST",
                "/auth/login",
                data={"username": email, "password": password}
            )
            
            if "access_token" in response:
                # Store session
                user_sessions[user_id] = {
                    "access_token": response["access_token"],
                    "refresh_token": response.get("refresh_token", ""),
                    "user_id": response.get("user_id", ""),
                }
                
                await update.message.reply_text(
                    f"{emoji.emojize(':check_mark:')} Login successful! Welcome back."
                )
            else:
                await update.message.reply_text(
                    f"{emoji.emojize(':cross_mark:')} Login failed: {response.get('detail', 'Invalid credentials')}"
                )
            return
    
    # Default response for other messages
    await update.message.reply_text(
        f"{emoji.emojize(':information:')} I don't understand that command. Use /help to see available commands."
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors in the bot.
    """
    logger.error(f"Error: {context.error}")
    
    # Send error message to user
    if update:
        await update.effective_message.reply_text(
            f"{emoji.emojize(':cross_mark:')} An error occurred: {context.error}"
        )


def main() -> None:
    """
    Main function to start the bot.
    """
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("login", login_command))
    application.add_handler(CommandHandler("logout", logout_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("services", services_command))
    application.add_handler(CommandHandler("orders", orders_command))
    application.add_handler(CommandHandler("clients", clients_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("servers", servers_command))
    application.add_handler(CommandHandler("locations", locations_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == "__main__":
    main() 