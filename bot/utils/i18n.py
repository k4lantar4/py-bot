"""
Internationalization (i18n) utilities for the V2Ray Telegram bot.

This module provides functions for managing translations and language preferences.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path

from utils.database import get_user_preferences, update_user_preferences

logger = logging.getLogger(__name__)

# Load translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {}
AVAILABLE_LANGUAGES = {
    "en": "English",
    "fa": "فارسی"
}

def load_translations() -> None:
    """Load all translation files."""
    i18n_dir = Path(__file__).parent.parent / "i18n"
    
    for lang_code in AVAILABLE_LANGUAGES.keys():
        file_path = i18n_dir / f"{lang_code}.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                TRANSLATIONS[lang_code] = json.load(f)
            logger.info(f"Loaded translations for {lang_code}")
        except Exception as e:
            logger.error(f"Error loading translations for {lang_code}: {e}")
            # Load English as fallback
            if lang_code != "en":
                TRANSLATIONS[lang_code] = TRANSLATIONS.get("en", {})

def get_text(key: str, language: str = "en", **kwargs) -> str:
    """
    Get translated text for a given key.
    
    Args:
        key: The translation key to look up
        language: The language code (defaults to English)
        **kwargs: Format arguments for the translation string
    
    Returns:
        The translated text, formatted with any provided arguments
    """
    # Ensure translations are loaded
    if not TRANSLATIONS:
        load_translations()
    
    # Get translation
    try:
        text = TRANSLATIONS.get(language, {}).get(key)
        if not text:
            # Fallback to English
            text = TRANSLATIONS.get("en", {}).get(key, key)
        
        # Format with provided arguments
        if kwargs:
            text = text.format(**kwargs)
        
        return text
    except Exception as e:
        logger.error(f"Error getting translation for {key} in {language}: {e}")
        return key

def get_available_languages() -> Dict[str, str]:
    """Get dictionary of available languages."""
    return AVAILABLE_LANGUAGES

def set_user_language(user_id: int, language: str) -> None:
    """
    Set a user's preferred language.
    
    Args:
        user_id: The Telegram user ID
        language: The language code to set
    
    Raises:
        ValueError: If the language code is not supported
    """
    if language not in AVAILABLE_LANGUAGES:
        raise ValueError(f"Unsupported language code: {language}")
    
    try:
        preferences = get_user_preferences(user_id)
        preferences["language"] = language
        update_user_preferences(user_id, preferences)
        logger.info(f"Updated language preference for user {user_id} to {language}")
    except Exception as e:
        logger.error(f"Error setting language for user {user_id}: {e}")
        raise

def get_user_language(user_id: int) -> str:
    """
    Get a user's preferred language.
    
    Args:
        user_id: The Telegram user ID
    
    Returns:
        The user's preferred language code, defaults to English
    """
    try:
        preferences = get_user_preferences(user_id)
        return preferences.get("language", "en")
    except Exception as e:
        logger.error(f"Error getting language for user {user_id}: {e}")
        return "en"

def format_number(number: float, language: str = "en") -> str:
    """
    Format a number according to the language's conventions.
    
    Args:
        number: The number to format
        language: The language code
    
    Returns:
        The formatted number as a string
    """
    if language == "fa":
        # Convert to Persian numerals
        persian_numerals = {
            "0": "۰", "1": "۱", "2": "۲", "3": "۳", "4": "۴",
            "5": "۵", "6": "۶", "7": "۷", "8": "۸", "9": "۹",
            ".": "٫"  # Persian decimal separator
        }
        formatted = f"{number:,.2f}"  # Format with commas and 2 decimal places
        return "".join(persian_numerals.get(c, c) for c in formatted)
    
    return f"{number:,.2f}"

def format_date(date: str, language: str = "en") -> str:
    """
    Format a date string according to the language's conventions.
    
    Args:
        date: The date string to format (ISO format)
        language: The language code
    
    Returns:
        The formatted date as a string
    """
    from datetime import datetime
    from jdatetime import datetime as jdatetime
    
    try:
        dt = datetime.fromisoformat(date)
        
        if language == "fa":
            # Convert to Jalali calendar
            jdt = jdatetime.fromgregorian(datetime=dt)
            return jdt.strftime("%Y/%m/%d %H:%M")
        
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        logger.error(f"Error formatting date {date}: {e}")
        return date

# Load translations on module import
load_translations() 