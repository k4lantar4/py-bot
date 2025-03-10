"""
User command handlers for the bot.
"""

from telegram import Update
from telegram.ext import ContextTypes
from ..utils.i18n import i18n
from ..utils.decorators import auth_required
from ..services.user_service import user_service
from ..keyboards.base import create_inline_keyboard

@auth_required
async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /services command."""
    user_id = update.effective_user.id
    session = context.bot_data["user_sessions"][user_id]
    
    response = await user_service.get_services(session["access_token"])
    
    if "detail" in response:
        await update.message.reply_text(
            i18n.get_text("errors.api_error", error=response["detail"])
        )
        return
    
    if not response:
        await update.message.reply_text("No services found.")
        return
    
    # Format services list
    services_text = "📋 *Your Services*\n\n"
    for service in response:
        services_text += (
            f"🔹 *{service['name']}*\n"
            f"  • Status: {service['status']}\n"
            f"  • Expires: {service.get('expiry_date', 'N/A')}\n"
            f"  • Traffic: {service.get('traffic_used', 0)}/{service.get('traffic_limit', 'Unlimited')}\n\n"
        )
    
    await update.message.reply_text(
        services_text,
        parse_mode="Markdown"
    )

@auth_required
async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /orders command."""
    user_id = update.effective_user.id
    session = context.bot_data["user_sessions"][user_id]
    
    response = await user_service.get_orders(session["access_token"])
    
    if "detail" in response:
        await update.message.reply_text(
            i18n.get_text("errors.api_error", error=response["detail"])
        )
        return
    
    if not response:
        await update.message.reply_text("No orders found.")
        return
    
    # Format orders list
    orders_text = "📦 *Your Orders*\n\n"
    for order in response:
        orders_text += (
            f"🔸 *Order #{order['id']}*\n"
            f"  • Service: {order['service_name']}\n"
            f"  • Status: {order['status']}\n"
            f"  • Date: {order['created_at']}\n"
            f"  • Amount: ${order['amount']}\n\n"
        )
    
    await update.message.reply_text(
        orders_text,
        parse_mode="Markdown"
    )

@auth_required
async def clients_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /clients command."""
    user_id = update.effective_user.id
    session = context.bot_data["user_sessions"][user_id]
    
    response = await user_service.get_clients(session["access_token"])
    
    if "detail" in response:
        await update.message.reply_text(
            i18n.get_text("errors.api_error", error=response["detail"])
        )
        return
    
    if not response:
        await update.message.reply_text("No clients found.")
        return
    
    # Format clients list
    clients_text = "👥 *Your Clients*\n\n"
    for client in response:
        clients_text += (
            f"👤 *{client['name']}*\n"
            f"  • Email: {client['email']}\n"
            f"  • Status: {client['status']}\n"
            f"  • Services: {len(client.get('services', []))}\n\n"
        )
    
    await update.message.reply_text(
        clients_text,
        parse_mode="Markdown"
    ) 