"""
Authentication command handlers for the bot.
"""

from telegram import Update
from telegram.ext import ContextTypes
import emoji
from ..utils.i18n import i18n
from ..utils.api import api_client
from ..utils.decorators import auth_required

async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /login command."""
    user_id = update.effective_user.id
    
    # Check if already logged in
    if user_id in context.bot_data.get("user_sessions", {}):
        await update.message.reply_text(
            i18n.get_text("auth.already_logged_in")
        )
        return
    
    # Ask for email
    await update.message.reply_text(
        i18n.get_text("auth.enter_email")
    )
    
    # Store the current state
    context.user_data["auth_state"] = "waiting_for_email"

async def handle_login_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the login flow states."""
    user_id = update.effective_user.id
    message_text = update.message.text
    auth_state = context.user_data.get("auth_state")
    
    if auth_state == "waiting_for_email":
        # Store email and ask for password
        context.user_data["email"] = message_text
        context.user_data["auth_state"] = "waiting_for_password"
        await update.message.reply_text(
            i18n.get_text("auth.enter_password")
        )
        
    elif auth_state == "waiting_for_password":
        # Try to login with provided credentials
        email = context.user_data.get("email")
        password = message_text
        
        # Clean up sensitive data
        del context.user_data["email"]
        del context.user_data["auth_state"]
        
        # Call login API
        response = await api_client.request(
            "POST",
            "/auth/login",
            data={"email": email, "password": password}
        )
        
        if "access_token" in response:
            # Store session
            if "user_sessions" not in context.bot_data:
                context.bot_data["user_sessions"] = {}
            context.bot_data["user_sessions"][user_id] = {
                "access_token": response["access_token"],
                "email": email
            }
            
            await update.message.reply_text(
                i18n.get_text("auth.login_success")
            )
        else:
            await update.message.reply_text(
                i18n.get_text("auth.login_failed")
            )

@auth_required
async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /logout command."""
    user_id = update.effective_user.id
    
    # Remove session
    if "user_sessions" in context.bot_data and user_id in context.bot_data["user_sessions"]:
        del context.bot_data["user_sessions"][user_id]
    
    await update.message.reply_text(
        i18n.get_text("auth.logout_success")
    )

@auth_required
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /profile command."""
    user_id = update.effective_user.id
    session = context.bot_data["user_sessions"][user_id]
    
    # Get user profile from API
    response = await api_client.request(
        "GET",
        "/users/me",
        token=session["access_token"]
    )
    
    if "detail" in response:
        await update.message.reply_text(
            i18n.get_text("errors.api_error", error=response["detail"])
        )
        return
    
    # Format profile information
    profile_text = (
        f"👤 *Profile Information*\n\n"
        f"Email: `{response['email']}`\n"
        f"Name: {response.get('full_name', 'N/A')}\n"
        f"Role: {response.get('role', 'User')}\n"
        f"Created: {response.get('created_at', 'N/A')}"
    )
    
    await update.message.reply_text(
        profile_text,
        parse_mode="Markdown"
    ) 