"""
Server monitoring handler for the V2Ray Telegram bot.

This module implements handlers for server monitoring operations including:
- Server health checks
- Traffic statistics
- System resource monitoring
- Server status updates
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode

from utils.i18n import get_text, format_number, format_date
from utils.database import get_user, get_all_servers, get_server_health
from utils.xui_api import XUIClient
from utils.decorators import require_admin

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_ACTION = 0

# Callback data patterns
MONITORING_CB = "monitoring"
SERVER_STATUS = f"{MONITORING_CB}_status"
TRAFFIC_STATS = f"{MONITORING_CB}_traffic"
SYSTEM_STATS = f"{MONITORING_CB}_system"
REFRESH_STATS = f"{MONITORING_CB}_refresh"

@require_admin
async def monitoring_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the monitoring menu."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    text = get_text("monitoring_menu_info", language_code)
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("server_status", language_code),
                callback_data=SERVER_STATUS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("traffic_stats", language_code),
                callback_data=TRAFFIC_STATS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("system_stats", language_code),
                callback_data=SYSTEM_STATS
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

@require_admin
async def server_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show server status information."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Get all servers
    servers = get_all_servers()
    
    if not servers:
        text = get_text("no_servers", language_code)
    else:
        text = get_text("server_status_header", language_code) + "\n\n"
        
        for server in servers:
            # Get server health
            health = get_server_health(server["id"])
            
            # Get server status from 3x-UI
            try:
                xui_client = XUIClient(
                    base_url=server["panel_url"],
                    username=server["panel_username"],
                    password=server["panel_password"]
                )
                status = xui_client.get_server_status()
                
                text += get_text("server_status_item", language_code).format(
                    name=server["name"],
                    status="🟢" if health["is_healthy"] else "🔴",
                    uptime=status.get("uptime", "N/A"),
                    load=status.get("load", "N/A"),
                    memory_used=format_number(status.get("memory_used", 0), language_code),
                    memory_total=format_number(status.get("memory_total", 0), language_code),
                    disk_used=format_number(status.get("disk_used", 0), language_code),
                    disk_total=format_number(status.get("disk_total", 0), language_code),
                    cpu_usage=format_number(status.get("cpu_usage", 0), language_code)
                )
            except Exception as e:
                logger.error(f"Error getting status for server {server['name']}: {e}")
                text += get_text("server_status_error", language_code).format(
                    name=server["name"],
                    error=str(e)
                )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("refresh", language_code),
                callback_data=REFRESH_STATS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_monitoring", language_code),
                callback_data=MONITORING_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

@require_admin
async def traffic_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show traffic statistics."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Get all servers
    servers = get_all_servers()
    
    if not servers:
        text = get_text("no_servers", language_code)
    else:
        text = get_text("traffic_stats_header", language_code) + "\n\n"
        total_up = 0
        total_down = 0
        
        for server in servers:
            try:
                xui_client = XUIClient(
                    base_url=server["panel_url"],
                    username=server["panel_username"],
                    password=server["panel_password"]
                )
                
                # Get inbounds for traffic stats
                inbounds = xui_client.get_inbounds()
                server_up = 0
                server_down = 0
                
                for inbound in inbounds:
                    server_up += inbound.get("up", 0)
                    server_down += inbound.get("down", 0)
                
                total_up += server_up
                total_down += server_down
                
                text += get_text("server_traffic_item", language_code).format(
                    name=server["name"],
                    up=format_number(server_up / (1024 * 1024 * 1024), language_code),  # Convert to GB
                    down=format_number(server_down / (1024 * 1024 * 1024), language_code),  # Convert to GB
                    total=format_number((server_up + server_down) / (1024 * 1024 * 1024), language_code)  # Convert to GB
                )
            except Exception as e:
                logger.error(f"Error getting traffic stats for server {server['name']}: {e}")
                text += get_text("server_traffic_error", language_code).format(
                    name=server["name"],
                    error=str(e)
                )
        
        # Add total traffic stats
        text += "\n" + get_text("total_traffic_stats", language_code).format(
            up=format_number(total_up / (1024 * 1024 * 1024), language_code),  # Convert to GB
            down=format_number(total_down / (1024 * 1024 * 1024), language_code),  # Convert to GB
            total=format_number((total_up + total_down) / (1024 * 1024 * 1024), language_code)  # Convert to GB
        )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("refresh", language_code),
                callback_data=REFRESH_STATS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_monitoring", language_code),
                callback_data=MONITORING_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

@require_admin
async def system_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show system statistics."""
    query = update.callback_query
    await query.answer()
    
    language_code = context.user_data.get("language", "en")
    
    # Get all servers
    servers = get_all_servers()
    
    if not servers:
        text = get_text("no_servers", language_code)
    else:
        text = get_text("system_stats_header", language_code) + "\n\n"
        
        for server in servers:
            try:
                xui_client = XUIClient(
                    base_url=server["panel_url"],
                    username=server["panel_username"],
                    password=server["panel_password"]
                )
                
                # Get server status and health
                status = xui_client.get_server_status()
                health = get_server_health(server["id"])
                
                # Get inbounds count
                inbounds = xui_client.get_inbounds()
                active_clients = sum(len(inbound.get("clientStats", [])) for inbound in inbounds)
                
                text += get_text("server_system_item", language_code).format(
                    name=server["name"],
                    status="🟢" if health["is_healthy"] else "🔴",
                    uptime=status.get("uptime", "N/A"),
                    load=status.get("load", "N/A"),
                    memory_used=format_number(status.get("memory_used", 0), language_code),
                    memory_total=format_number(status.get("memory_total", 0), language_code),
                    disk_used=format_number(status.get("disk_used", 0), language_code),
                    disk_total=format_number(status.get("disk_total", 0), language_code),
                    cpu_usage=format_number(status.get("cpu_usage", 0), language_code),
                    active_clients=active_clients,
                    inbounds_count=len(inbounds)
                )
            except Exception as e:
                logger.error(f"Error getting system stats for server {server['name']}: {e}")
                text += get_text("server_system_error", language_code).format(
                    name=server["name"],
                    error=str(e)
                )
    
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("refresh", language_code),
                callback_data=REFRESH_STATS
            )
        ],
        [
            InlineKeyboardButton(
                get_text("back_to_monitoring", language_code),
                callback_data=MONITORING_CB
            )
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    return SELECTING_ACTION

@require_admin
async def refresh_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Refresh the current statistics view."""
    query = update.callback_query
    callback_data = query.data
    
    # Determine which view to refresh based on user's context
    if "status" in context.user_data.get("last_monitoring_view", ""):
        return await server_status(update, context)
    elif "traffic" in context.user_data.get("last_monitoring_view", ""):
        return await traffic_stats(update, context)
    else:
        return await system_stats(update, context)

def get_monitoring_handler() -> ConversationHandler:
    """Create and return the monitoring conversation handler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(monitoring_menu, pattern=f"^{MONITORING_CB}$")
        ],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(server_status, pattern=f"^{SERVER_STATUS}$"),
                CallbackQueryHandler(traffic_stats, pattern=f"^{TRAFFIC_STATS}$"),
                CallbackQueryHandler(system_stats, pattern=f"^{SYSTEM_STATS}$"),
                CallbackQueryHandler(refresh_stats, pattern=f"^{REFRESH_STATS}$"),
                CallbackQueryHandler(monitoring_menu, pattern=f"^{MONITORING_CB}$"),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(monitoring_menu, pattern="^menu$"),
        ],
        name="monitoring",
        persistent=True
    ) 