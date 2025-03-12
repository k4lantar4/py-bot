"""
Configuration utilities for the Telegram bot.

This module provides functions for loading and managing configuration settings.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("telegram_bot")

# Default configuration
DEFAULT_CONFIG = {
    "admin_ids": [],
    "card_payment": {
        "card_number": "",
        "card_holder": "",
        "verification_timeout_minutes": 30
    },
    "zarinpal": {
        "enabled": False,
        "merchant_id": "",
        "sandbox": True,
        "callback_url": ""
    },
    "threexui": {
        "api_timeout": 30,
        "session_expiry": 3600
    }
}


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and return as a dictionary.
    
    Returns:
        Dictionary containing configuration settings
    """
    config = DEFAULT_CONFIG.copy()
    
    # Load admin user IDs
    admin_ids_str = os.getenv("ADMIN_USER_IDS", "[]")
    try:
        config["admin_ids"] = json.loads(admin_ids_str)
    except json.JSONDecodeError:
        logger.error(f"Invalid ADMIN_USER_IDS format: {admin_ids_str}. Using default: []")
    
    # Load card payment configuration
    config["card_payment"]["card_number"] = os.getenv("CARD_NUMBER", "")
    config["card_payment"]["card_holder"] = os.getenv("CARD_HOLDER", "")
    config["card_payment"]["verification_timeout_minutes"] = int(os.getenv("CARD_PAYMENT_VERIFICATION_TIMEOUT_MINUTES", "30"))
    
    # Load Zarinpal configuration
    config["zarinpal"]["enabled"] = bool(os.getenv("ZARINPAL_MERCHANT_ID", ""))
    config["zarinpal"]["merchant_id"] = os.getenv("ZARINPAL_MERCHANT_ID", "")
    config["zarinpal"]["sandbox"] = os.getenv("ZARINPAL_SANDBOX", "True").lower() == "true"
    config["zarinpal"]["callback_url"] = os.getenv("ZARINPAL_CALLBACK_URL", "")
    
    # Load 3X-UI configuration
    config["threexui"]["api_timeout"] = int(os.getenv("THREEXUI_API_TIMEOUT", "30"))
    config["threexui"]["session_expiry"] = int(os.getenv("THREEXUI_SESSION_EXPIRY", "3600"))
    
    # Load from database if available
    try:
        from utils.database import get_setting
        
        # Card payment details
        card_payment_details = get_setting("card_payment_details")
        if card_payment_details:
            try:
                card_details = json.loads(card_payment_details)
                if "card_number" in card_details:
                    config["card_payment"]["card_number"] = card_details["card_number"]
                if "card_holder" in card_details:
                    config["card_payment"]["card_holder"] = card_details["card_holder"]
            except json.JSONDecodeError:
                logger.error(f"Invalid card_payment_details format in database: {card_payment_details}")
        
        # Zarinpal details
        zarinpal_details = get_setting("zarinpal_payment_details")
        if zarinpal_details:
            try:
                zarinpal = json.loads(zarinpal_details)
                if "merchant_id" in zarinpal:
                    config["zarinpal"]["merchant_id"] = zarinpal["merchant_id"]
                    config["zarinpal"]["enabled"] = bool(zarinpal["merchant_id"])
            except json.JSONDecodeError:
                logger.error(f"Invalid zarinpal_payment_details format in database: {zarinpal_details}")
        
        # Admin user IDs
        admin_user_ids = get_setting("admin_user_ids")
        if admin_user_ids:
            try:
                admin_ids = json.loads(admin_user_ids)
                if isinstance(admin_ids, list):
                    config["admin_ids"] = admin_ids
            except json.JSONDecodeError:
                logger.error(f"Invalid admin_user_ids format in database: {admin_user_ids}")
        
    except ImportError:
        logger.warning("Database module not available, using configuration from environment variables only")
    except Exception as e:
        logger.error(f"Error loading configuration from database: {e}")
    
    # Validate configuration
    if not config["card_payment"]["card_number"] or not config["card_payment"]["card_holder"]:
        logger.warning("Card payment details not configured")
    
    if not config["zarinpal"]["merchant_id"]:
        logger.warning("Zarinpal merchant ID not configured")
    
    if not config["admin_ids"]:
        logger.warning("No admin users configured")
    
    return config


def is_admin(user_id: int) -> bool:
    """
    Check if the user is an admin.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if the user is an admin, False otherwise
    """
    try:
        # First, check in the database
        from utils.database import get_user
        user = get_user(user_id)
        if user and user.get("is_admin", False):
            return True
        
        # Then, check in the config
        config = load_config()
        return str(user_id) in map(str, config["admin_ids"])
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


def get_card_payment_details() -> Dict[str, Any]:
    """
    Get card payment details.
    
    Returns:
        Dictionary containing card payment details
    """
    config = load_config()
    return config["card_payment"]


def get_zarinpal_details() -> Dict[str, Any]:
    """
    Get Zarinpal payment details.
    
    Returns:
        Dictionary containing Zarinpal payment details
    """
    config = load_config()
    return config["zarinpal"]


def get_threexui_config() -> Dict[str, Any]:
    """
    Get 3X-UI API configuration.
    
    Returns:
        Dictionary containing 3X-UI API configuration
    """
    config = load_config()
    return config["threexui"] 