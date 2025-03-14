"""
Notification services for Telegram
"""
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from telegram.error import TelegramError
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)
User = get_user_model()

class NotificationService:
    """Base notification service"""
    
    def __init__(self):
        """Initialize the notification service"""
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.notifications_enabled = getattr(settings, 'TELEGRAM_NOTIFICATIONS_ENABLED', False)
        self.bot = None
        
        # Initialize bot if notifications are enabled
        if self.notifications_enabled and self.bot_token:
            try:
                from telegram import Bot
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram notification service initialized")
            except ImportError:
                logger.warning("python-telegram-bot is not installed, notifications will not be sent")
            except Exception as e:
                logger.error(f"Error initializing Telegram bot: {str(e)}")
        else:
            logger.info("Telegram notifications are disabled or bot token is not set")
    
    def send_message(self, chat_id, message):
        """
        Send a message to a specific chat ID
        
        Args:
            chat_id (int): Telegram chat ID
            message (str): Message text to send
        
        Returns:
            bool: Success status
        """
        if not self.bot or not self.notifications_enabled:
            logger.info("Notifications are disabled or bot not initialized")
            return False
        
        try:
            self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except TelegramError as e:
            logger.error(f"Telegram error sending message to {chat_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {str(e)}")
            return False


class AdminNotificationService(NotificationService):
    """Service for sending notifications to admin users"""
    
    def __init__(self):
        """Initialize the admin notification service"""
        super().__init__()
        self.admin_chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', None)
    
    def send_message(self, message):
        """
        Send a notification message to all admin users or to admin group chat
        
        Args:
            message (str): Message to send
            
        Returns:
            bool: Success status
        """
        if not self.bot or not self.notifications_enabled:
            logger.info("Notifications are disabled or bot not initialized")
            return False
        
        # If admin chat ID is set, send to that chat
        if self.admin_chat_id:
            return super().send_message(self.admin_chat_id, message)
        
        # Otherwise, send to all admin users with telegram_id
        try:
            admin_users = User.objects.filter(is_staff=True).exclude(telegram_id__isnull=True)
            
            if not admin_users.exists():
                logger.warning("No admin users with telegram_id found")
                return False
            
            success = False
            for admin in admin_users:
                if admin.telegram_id:
                    result = super().send_message(admin.telegram_id, message)
                    if result:
                        success = True
            
            return success
        except Exception as e:
            logger.error(f"Error sending admin notifications: {str(e)}")
            return False


class UserNotificationService(NotificationService):
    """Service for sending notifications to regular users"""
    
    def send_message(self, user, message):
        """
        Send a notification message to a user
        
        Args:
            user (User): User object or ID
            message (str): Message to send
            
        Returns:
            bool: Success status
        """
        if not self.bot or not self.notifications_enabled:
            logger.info("Notifications are disabled or bot not initialized")
            return False
        
        try:
            # Get user object if ID was passed
            if not isinstance(user, User):
                user = User.objects.get(id=user)
            
            # Make sure user has a telegram_id
            if not user.telegram_id:
                logger.warning(f"User {user.id} has no telegram_id, notification not sent")
                return False
            
            return super().send_message(user.telegram_id, message)
        except User.DoesNotExist:
            logger.error(f"User not found for notification")
            return False
        except Exception as e:
            logger.error(f"Error sending user notification: {str(e)}")
            return False 