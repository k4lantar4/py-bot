"""
Configuration settings for the Telegram bot.
"""

import os
from pathlib import Path
from typing import List
import json
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Bot configuration settings."""
    
    # Bot settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_USER_IDS: List[int] = json.loads(os.getenv("ADMIN_USER_IDS", "[]"))
    
    # API settings
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    API_TIMEOUT: float = 30.0
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    I18N_DIR: Path = BASE_DIR / "i18n"
    
    # Language settings
    DEFAULT_LANGUAGE: str = "fa"
    AVAILABLE_LANGUAGES: List[str] = ["fa", "en"]
    
    class Config:
        case_sensitive = True

# Create global settings instance
settings = Settings() 