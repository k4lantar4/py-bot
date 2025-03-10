"""
Admin command handlers for the bot.
"""

from telegram import Update
from telegram.ext import ContextTypes
from ..utils.i18n import i18n
from ..utils.decorators import admin_required, auth_required
from ..services.admin_service import admin_service
from ..keyboards.base import create_inline_keyboard

@admin_required
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /users command."""
    user_id = update.effective_user.id
    session = context.bot_data["user_sessions"][user_id]
    
    # Get page from context or default to 1
    page = context.user_data.get("users_page", 1)
    
    response = await admin_service.get_users(session["access_token"], page=page)
    
    if "detail" in response:
        await update.message.reply_text(
            i18n.get_text("errors.api_error", error=response["detail"])
        )
        return
    
    if not response.get("items"):
        await update.message.reply_text("No users found.")
        return
    
    # Format users list
    users_text = "👥 *Users List*\n\n"
    for user in response["items"]:
        users_text += (
            f"👤 *{user['email']}*\n"
            f"  • Name: {user.get('full_name', 'N/A')}\n"
            f"  • Role: {user.get('role', 'User')}\n"
            f"  • Status: {user['status']}\n\n"
        )
    
    # Add pagination info
    total_pages = (response["total"] + response["limit"] - 1) // response["limit"]
    users_text += f"\nPage {page} of {total_pages}"
    
    # Create pagination keyboard
    keyboard = []
    if page > 1:
        keyboard.append([{"text": "◀️ Previous", "callback_data": f"users_page:{page-1}"}])
    if page < total_pages:
        keyboard.append([{"text": "Next ▶️", "callback_data": f"users_page:{page+1}"}])
    
    await update.message.reply_text(
        users_text,
        parse_mode="Markdown",
        reply_markup=create_inline_keyboard(keyboard) if keyboard else None
    )

@admin_required
async def servers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /servers command."""
    user_id = update.effective_user.id
    session = context.bot_data["user_sessions"][user_id]
    
    response = await admin_service.get_servers(session["access_token"])
    
    if "detail" in response:
        await update.message.reply_text(
            i18n.get_text("errors.api_error", error=response["detail"])
        )
        return
    
    if not response:
        await update.message.reply_text("No servers found.")
        return
    
    # Format servers list
    servers_text = "🖥️ *Servers List*\n\n"
    for server in response:
        # Get server status
        status = await admin_service.get_server_status(
            session["access_token"],
            server["id"]
        )
        
        servers_text += (
            f"🔹 *{server['name']}*\n"
            f"  • IP: {server['ip']}\n"
            f"  • Location: {server.get('location', 'N/A')}\n"
            f"  • Status: {status.get('status', 'Unknown')}\n"
            f"  • Load: {status.get('load', 'N/A')}\n"
            f"  • Memory: {status.get('memory_used', 0)}/{status.get('memory_total', 0)} MB\n\n"
        )
    
    await update.message.reply_text(
        servers_text,
        parse_mode="Markdown"
    )

@admin_required
async def locations_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /locations command."""
    user_id = update.effective_user.id
    session = context.bot_data["user_sessions"][user_id]
    
    response = await admin_service.get_locations(session["access_token"])
    
    if "detail" in response:
        await update.message.reply_text(
            i18n.get_text("errors.api_error", error=response["detail"])
        )
        return
    
    if not response:
        await update.message.reply_text("No locations found.")
        return
    
    # Format locations list
    locations_text = "🌍 *Locations List*\n\n"
    for location in response:
        locations_text += (
            f"📍 *{location['name']}*\n"
            f"  • Country: {location['country']}\n"
            f"  • City: {location['city']}\n"
            f"  • Servers: {len(location.get('servers', []))}\n\n"
        )
    
    await update.message.reply_text(
        locations_text,
        parse_mode="Markdown"
    )

@admin_required
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /stats command."""
    user_id = update.effective_user.id
    session = context.bot_data["user_sessions"][user_id]
    
    response = await admin_service.get_system_stats(session["access_token"])
    
    if "detail" in response:
        await update.message.reply_text(
            i18n.get_text("errors.api_error", error=response["detail"])
        )
        return
    
    # Format system statistics
    stats_text = "📊 *System Statistics*\n\n"
    stats_text += (
        f"👥 Users: {response.get('total_users', 0)}\n"
        f"🔌 Active Services: {response.get('active_services', 0)}\n"
        f"📦 Total Orders: {response.get('total_orders', 0)}\n"
        f"💰 Monthly Revenue: ${response.get('monthly_revenue', 0)}\n\n"
        f"🖥️ System Info:\n"
        f"  • CPU Usage: {response.get('cpu_usage', 0)}%\n"
        f"  • Memory Usage: {response.get('memory_usage', 0)}%\n"
        f"  • Disk Usage: {response.get('disk_usage', 0)}%\n"
    )
    
    await update.message.reply_text(
        stats_text,
        parse_mode="Markdown"
    ) 