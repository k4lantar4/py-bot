"""
Internationalization utilities.
"""

import json
import logging
from typing import Dict, Any
from pathlib import Path
from ..config.settings import settings

logger = logging.getLogger(__name__)

class I18nManager:
    """Manager for handling internationalization."""
    
    def __init__(self):
        """Initialize the I18n manager."""
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files."""
        for lang in settings.AVAILABLE_LANGUAGES:
            try:
                file_path = settings.I18N_DIR / f"{lang}.json"
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
                logger.info(f"Loaded translations for language: {lang}")
            except Exception as e:
                logger.error(f"Failed to load translations for {lang}: {e}")
                self.translations[lang] = {}
    
    def get_text(self, key: str, lang: str = None, **kwargs) -> str:
        """
        Get translated text for a key.
        
        Args:
            key: Translation key (dot notation supported, e.g. 'auth.login_success')
            lang: Language code (defaults to DEFAULT_LANGUAGE)
            **kwargs: Format arguments for the translation string
            
        Returns:
            Translated text
        """
        lang = lang or settings.DEFAULT_LANGUAGE
        if lang not in self.translations:
            lang = settings.DEFAULT_LANGUAGE
        
        # Split key by dots and traverse the translations dict
        current = self.translations[lang]
        for part in key.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                logger.warning(f"Translation key not found: {key} (lang: {lang})")
                return key
        
        # If we got a string, format it with kwargs
        if isinstance(current, str):
            try:
                return current % kwargs if kwargs else current
            except Exception as e:
                logger.error(f"Failed to format translation: {e}")
                return current
        
        return key

# Create global i18n manager instance
i18n = I18nManager() 